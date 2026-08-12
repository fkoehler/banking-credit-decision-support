from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    app_env: str = "local"
    database_url: str = "postgresql://localhost:5432/bank_credit_support"
    ai_model_path: Path = Path("artifacts/risk-model.joblib")
    ai_model_metadata_path: Path = Path("artifacts/metrics.json")
    ai_inference_provider: str = "local"
    ai_embedding_provider: str = "local"
    ai_generation_provider: str = "template"
    ai_vector_store: str = "postgres"
    ai_local_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ai_embedding_dimensions: int = 384
    ai_chunk_size: int = 700
    ai_chunk_overlap: int = 100
    ai_rag_top_k: int = 5
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = ""
    azure_openai_chat_deployment: str = ""
    azure_openai_embedding_deployment: str = ""
    azure_ml_endpoint: str = ""
    azure_ml_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
