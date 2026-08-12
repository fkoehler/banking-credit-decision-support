from fastembed import TextEmbedding

from bank_ai.config import Settings
from bank_ai.rag import chunk_document


def test_chunking_preserves_headings_and_overlap():
    chunks = chunk_document("# Equity\n" + " ".join(f"word{i}" for i in range(30)), 12, 3)

    assert len(chunks) == 3
    assert all(section == "Equity" for section, _ in chunks)
    assert chunks[0][1].split()[-3:] == chunks[1][1].split()[:3]


def test_default_embedding_model_is_supported_and_matches_vector_dimension():
    settings = Settings()
    supported = {model["model"]: model["dim"] for model in TextEmbedding.list_supported_models()}

    assert supported[settings.ai_local_embedding_model] == settings.ai_embedding_dimensions
