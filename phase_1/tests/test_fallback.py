import pytest
from src.utils.generator import _extractive_bullets

def test_no_chunks_returns_message():
    result = _extractive_bullets("test query", [])
    assert "No relevant information found" in result

def test_extractive_bullets_returns_bullets():
    chunks = [{
        "text": "Use bold, high-contrast faces in thumbnails.",
        "video_id": "video_1",
        "start": "00:00:01.000",
        "end": "00:00:05.000",
        "source": "video_1_transcript.txt"
    }]
    result = _extractive_bullets("thumbnails", chunks)
    assert result.startswith("-")
    assert "[source: video_1" in result