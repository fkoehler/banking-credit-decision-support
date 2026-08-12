from pathlib import Path

from bank_ai.config import get_settings
from bank_ai.models import DocumentRequest
from bank_ai.rag import RagEngine


def main() -> None:
    root = Path(__file__).resolve().parents[4]
    engine = RagEngine(get_settings())
    for path in sorted((root / "docs" / "policies").glob("*.md")):
        result = engine.ingest(
            DocumentRequest(title=path.stem.replace("-", " ").title(), content=path.read_text())
        )
        print(f"Indexed {result.title}: {result.chunkCount} chunks")


if __name__ == "__main__":
    main()

