import pytest
from src.utils.generator import _extractive_bullets

def test_citation_format():
    chunks = [{
        "text": "Mention retention in the first 10 seconds.",
        "video_id": "video_2",
        "start": "00:00:10.000",
        "end": "00:00:20.000",
        "source": "video_2_transcript.txt"
    }]
    result = _extractive_bullets("retention", chunks)
    assert "[source: video_2 t=00:00:10.000–00:00:20.000]" in result