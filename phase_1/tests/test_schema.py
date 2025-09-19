import pytest
import weaviate

def test_weaviate_schema_exists():
    client = weaviate.Client("http://127.0.0.1:8081")
    assert client.schema.exists("TranscriptChunk")

def test_weaviate_object_properties():
    client = weaviate.Client("http://127.0.0.1:8081")
    schema = client.schema.get("TranscriptChunk")
    prop_names = [p["name"] for p in schema["properties"]]
    for expected in ["text", "video_id", "start", "end", "source"]:
        assert expected in prop_names