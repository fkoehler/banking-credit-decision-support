from functools import lru_cache

from fastapi import FastAPI
from openai import OpenAIError

from bank_ai.config import Settings, get_settings
from bank_ai.generation import build_generator
from bank_ai.ml import RiskPredictor, build_risk_predictor, risk_band
from bank_ai.models import (
    AssessmentRequest,
    AssessmentResponse,
    DocumentRequest,
    DocumentResponse,
    DocumentSummary,
)
from bank_ai.rag import RagEngine, citations_from

app = FastAPI(
    title="Banking Credit AI Service",
    version="0.1.0",
    docs_url="/internal/docs",
    openapi_url="/internal/openapi.json",
)


@lru_cache
def risk_model() -> RiskPredictor:
    return build_risk_predictor(get_settings())


@lru_cache
def rag_engine() -> RagEngine:
    return RagEngine(get_settings())


@app.get("/internal/v1/health")
def health() -> dict[str, str]:
    return {"status": "UP"}


@app.post("/internal/v1/assess", response_model=AssessmentResponse)
def assess(request: AssessmentRequest) -> AssessmentResponse:
    settings = get_settings()
    probability, positives, risks = risk_model().predict(request)
    band = risk_band(probability)
    question = (
        f"Which fictional policies apply to a {request.profession} practice financing with "
        f"{request.equity:.0f} equity and {request.requestedCredit:.0f} requested credit?"
    )
    chunks = rag_engine().retrieve(question)
    try:
        generator = build_generator(settings)
        summary = generator.generate(probability, band, positives, risks, chunks)
        generation_mode = generator.mode
    except (OpenAIError, ValueError):
        fallback = build_generator(Settings(ai_generation_provider="template"))
        summary = "Generative explanation unavailable. " + fallback.generate(
            probability, band, positives, risks, chunks
        )
        generation_mode = "template-after-provider-error"
    return AssessmentResponse(
        riskProbability=round(probability, 6),
        riskBand=band,
        positiveFactors=positives,
        riskFactors=risks,
        summary=summary,
        citations=citations_from(chunks),
        generationMode=generation_mode,
        modelVersion=risk_model().version,
    )


@app.post("/internal/v1/documents", response_model=DocumentResponse)
def ingest_document(request: DocumentRequest) -> DocumentResponse:
    return rag_engine().ingest(request)


@app.get("/internal/v1/documents", response_model=list[DocumentSummary])
def list_documents() -> list[DocumentSummary]:
    return rag_engine().store.list_documents()
