from bank_ai.config import get_settings
from bank_ai.rag import PostgresVectorStore, build_embedding_provider


def main() -> None:
    settings = get_settings()
    embedding = build_embedding_provider(settings)
    vector = embedding.embed(["local bootstrap check"])[0]
    if len(vector) != settings.ai_embedding_dimensions:
        raise RuntimeError(
            "Embedding dimension mismatch: "
            f"expected {settings.ai_embedding_dimensions}, received {len(vector)}"
        )
    PostgresVectorStore(settings).ensure_schema()
    print(f"Embedding provider ready: {settings.ai_embedding_provider} ({len(vector)} dimensions)")


if __name__ == "__main__":
    main()
