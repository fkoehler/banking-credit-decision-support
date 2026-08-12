from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass

import numpy as np
import psycopg
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from pgvector.psycopg import register_vector

from bank_ai.config import Settings
from bank_ai.models import Citation, DocumentRequest, DocumentResponse, DocumentSummary


class EmbeddingProvider:
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        from fastembed import TextEmbedding

        self.model = TextEmbedding(model_name=model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        values = self.model.embed(texts)
        return [value.astype(float).tolist() for value in values]


class AzureEmbeddingProvider(EmbeddingProvider):
    def __init__(self, settings: Settings):
        credentials = (
            {
                "api_key": settings.azure_openai_api_key,
            }
            if settings.azure_openai_api_key
            else {
                "azure_ad_token_provider": get_bearer_token_provider(
                    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
                )
            }
        )
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            **credentials,
        )
        self.deployment = settings.azure_openai_embedding_deployment
        self.dimensions = settings.ai_embedding_dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.deployment, input=texts, dimensions=self.dimensions
        )
        return [item.embedding for item in response.data]


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.ai_embedding_provider == "azure-openai":
        return AzureEmbeddingProvider(settings)
    return LocalEmbeddingProvider(settings.ai_local_embedding_model)


@dataclass
class RetrievedChunk:
    document_id: str
    title: str
    section: str
    content: str
    score: float


class PostgresVectorStore:
    def __init__(self, settings: Settings):
        self.database_url = settings.database_url
        self.dimensions = settings.ai_embedding_dimensions

    def _connection(self):
        connection = psycopg.connect(self.database_url)
        register_vector(connection)
        return connection

    def ensure_schema(self) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_documents (
                    id UUID PRIMARY KEY,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    checksum TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS ai_chunks (
                    id UUID PRIMARY KEY,
                    document_id UUID NOT NULL REFERENCES ai_documents(id) ON DELETE CASCADE,
                    ordinal INTEGER NOT NULL,
                    section TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector({self.dimensions}) NOT NULL,
                    UNIQUE(document_id, ordinal)
                )
                """
            )

    def save(
        self,
        request: DocumentRequest,
        checksum: str,
        chunks: list[tuple[str, str]],
        embeddings: list[list[float]],
    ) -> DocumentResponse:
        self.ensure_schema()
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT id FROM ai_documents WHERE checksum = %s", (checksum,)
            ).fetchone()
            if existing:
                document_id = str(existing[0])
                count = connection.execute(
                    "SELECT count(*) FROM ai_chunks WHERE document_id = %s", (existing[0],)
                ).fetchone()[0]
                return DocumentResponse(
                    documentId=document_id, title=request.title, checksum=checksum, chunkCount=count
                )
            document_id = uuid.uuid4()
            connection.execute(
                "INSERT INTO ai_documents(id, title, source, checksum) VALUES (%s, %s, %s, %s)",
                (document_id, request.title, request.source, checksum),
            )
            for ordinal, ((section, content), embedding) in enumerate(zip(chunks, embeddings)):
                connection.execute(
                    """
                    INSERT INTO ai_chunks(id, document_id, ordinal, section, content, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (uuid.uuid4(), document_id, ordinal, section, content, np.array(embedding)),
                )
            return DocumentResponse(
                documentId=str(document_id),
                title=request.title,
                checksum=checksum,
                chunkCount=len(chunks),
            )

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        self.ensure_schema()
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT d.id, d.title, c.section, c.content, 1 - (c.embedding <=> %s) AS score
                FROM ai_chunks c JOIN ai_documents d ON d.id = c.document_id
                ORDER BY c.embedding <=> %s LIMIT %s
                """,
                (np.array(query_embedding), np.array(query_embedding), top_k),
            ).fetchall()
        return [RetrievedChunk(str(row[0]), row[1], row[2], row[3], float(row[4])) for row in rows]

    def list_documents(self) -> list[DocumentSummary]:
        self.ensure_schema()
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT d.id, d.title, d.source, count(c.id)
                FROM ai_documents d LEFT JOIN ai_chunks c ON c.document_id = d.id
                GROUP BY d.id ORDER BY d.title
                """
            ).fetchall()
        return [
            DocumentSummary(documentId=str(row[0]), title=row[1], source=row[2], chunkCount=row[3])
            for row in rows
        ]


class RagEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embedding_provider = build_embedding_provider(settings)
        self.store = PostgresVectorStore(settings)

    def ingest(self, request: DocumentRequest) -> DocumentResponse:
        checksum = hashlib.sha256(request.content.encode()).hexdigest()
        chunks = chunk_document(
            request.content, self.settings.ai_chunk_size, self.settings.ai_chunk_overlap
        )
        embeddings = self.embedding_provider.embed([content for _, content in chunks])
        return self.store.save(request, checksum, chunks, embeddings)

    def retrieve(self, question: str) -> list[RetrievedChunk]:
        query_embedding = self.embedding_provider.embed([question])[0]
        return self.store.search(query_embedding, self.settings.ai_rag_top_k)


def chunk_document(content: str, chunk_size: int, overlap: int) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = "General"
    current_lines: list[str] = []
    for line in content.splitlines():
        heading = re.match(r"^#{1,4}\s+(.+)$", line.strip())
        if heading:
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = heading.group(1).strip()
            current_lines = []
        elif line.strip():
            current_lines.append(line.strip())
    if current_lines:
        sections.append((current_title, current_lines))

    result: list[tuple[str, str]] = []
    for title, lines in sections:
        words = " ".join(lines).split()
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            result.append((title, " ".join(words[start:end])))
            if end == len(words):
                break
            start = max(end - overlap, start + 1)
    return result


def citations_from(chunks: list[RetrievedChunk]) -> list[Citation]:
    return [
        Citation(
            documentId=chunk.document_id,
            title=chunk.title,
            section=chunk.section,
            score=round(chunk.score, 4),
        )
        for chunk in chunks
    ]
