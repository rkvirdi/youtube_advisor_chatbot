# src/utils/retriever.py
import os
import weaviate
from sentence_transformers import SentenceTransformer

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://127.0.0.1:8081")
CLASS_NAME   = os.getenv("WEAVIATE_CLASS_NAME", "TranscriptChunk")
EMBED_MODEL  = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

_client   = weaviate.Client(WEAVIATE_URL)
_embedder = SentenceTransformer(EMBED_MODEL)  
def retrieve_relevant_chunks(query: str, top_k: int = 5, alpha: float = 0.5):
    """
    Read-only retrieval.
    Uses BM25 + your query's semantic vector (computed in memory).
    """
    qvec = _embedder.encode(query).tolist()

    # Hybrid with BYO vector (works with vectorizer="none")
    result = (
        _client.query
        .get(CLASS_NAME, ["text", "video_id", "start", "end", "source"])
        .with_hybrid(query=query, alpha=alpha, vector=qvec)
        .with_limit(top_k)
        .with_additional(["score"])  # optional: see ranking score
        .do()
    )

    objs = (result.get("data", {}).get("Get", {}).get(CLASS_NAME, []) or [])
    return [
        {
            "text":   o.get("text", ""),
            "video_id": o.get("video_id", ""),
            "start":  o.get("start", ""),
            "end":    o.get("end", ""),
            "source": o.get("source", ""),
        }
        for o in objs
    ]


# import os
# import weaviate

# def retrieve_relevant_chunks(query, top_k=5):
# 	"""
# 	Hybrid retrieval from Weaviate using BM25 and semantic search.
# 	Returns top_k relevant transcript chunks with metadata.
# 	"""
# 	weaviate_url = os.getenv("WEAVIATE_URL")
# 	class_name = os.getenv("WEAVIATE_CLASS_NAME")

# 	client = weaviate.Client(weaviate_url)

# 	# Hybrid search: BM25 (keyword) + semantic (vector)
# 	response = client.query.get(class_name, ["text", "video_id", "start", "end", "source"])
# 	response = response.with_hybrid(query=query, alpha=0.5)
# 	response = response.with_limit(top_k)
# 	result = response.do()

# 	# Parse results
# 	chunks = []
# 	for obj in result.get("data", {}).get("Get", {}).get(class_name, []):
# 		chunks.append({
# 			"text": obj["text"],
# 			"video_id": obj["video_id"],
# 			"start": obj["start"],
# 			"end": obj["end"],
# 			"source": obj["source"]
# 		})
# 	return chunks
