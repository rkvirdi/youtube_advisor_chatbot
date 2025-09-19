import re
import pytest
from src.utils.retriever import retrieve_relevant_chunks
from src.utils.generator import generate_response


def test_retrieval_and_generation(monkeypatch):
    # Monkeypatch retriever to return a known chunk
    monkeypatch.setattr("src.utils.retriever.retrieve_relevant_chunks", lambda q, **kw: [{
        "text": "Test integration works.",
        "video_id": "video_1",
        "start": "00:00:01.000",
        "end": "00:00:05.000",
        "source": "video_1_transcript.txt"
    }])

    response = generate_response("integration", retrieve_relevant_chunks("integration"))

    # --- Option A: Behavioral checks ---
    # 1. Response should be a non-empty string
    assert isinstance(response, str)
    assert len(response.strip()) > 0

    # 2. Response should look like a bullet list
    assert response.strip().startswith("- ")

    # 3. Response should include at least one properly formatted citation
    citation_re = re.compile(
        r'\[source:\s.+?\st=\d{2}:\d{2}:\d{2}\.\d{3}–\d{2}:\d{2}:\d{2}\.\d{3}\]'
    )
    assert citation_re.search(response) is not None
