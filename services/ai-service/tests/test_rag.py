from bank_ai.rag import chunk_document


def test_chunking_preserves_headings_and_overlap():
    chunks = chunk_document("# Equity\n" + " ".join(f"word{i}" for i in range(30)), 12, 3)

    assert len(chunks) == 3
    assert all(section == "Equity" for section, _ in chunks)
    assert chunks[0][1].split()[-3:] == chunks[1][1].split()[:3]

