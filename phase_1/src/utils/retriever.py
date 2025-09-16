# src/utils/retriever.py
import os, weaviate
from sentence_transformers import SentenceTransformer

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://127.0.0.1:8081")
CLASS_NAME   = os.getenv("WEAVIATE_CLASS_NAME", "TranscriptChunk")
EMBED_MODEL  = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

_client   = weaviate.Client(WEAVIATE_URL)
_embedder = SentenceTransformer(EMBED_MODEL)

def retrieve_relevant_chunks(query: str, top_k: int = 15, alpha: float = 0.3):
    qvec = _embedder.encode(query).tolist()
    res = (
        _client.query.get(CLASS_NAME, ["text","video_id","start","end","source"])
        .with_hybrid(query=query, alpha=alpha, vector=qvec)  # BYO query vector
        .with_limit(top_k)
        .with_additional(["score"])
        .do()
    )
    objs = res.get("data", {}).get("Get", {}).get(CLASS_NAME, []) or []
    return [
        { "text": o.get("text",""), "video_id": o.get("video_id",""),
          "start": o.get("start",""), "end": o.get("end",""), "source": o.get("source","") }
        for o in objs
    ]
