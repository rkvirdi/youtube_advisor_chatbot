# scripts/retrieval_sanity.py
import os, weaviate
from sentence_transformers import SentenceTransformer

URL = os.getenv("WEAVIATE_URL", "http://127.0.0.1:8081")
CLS = os.getenv("WEAVIATE_CLASS_NAME", "TranscriptChunk")
MODEL = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

client = weaviate.Client(URL)
embed = SentenceTransformer(MODEL)

q = "how to write a strong introduction with a hook"
qvec = embed.encode(q).tolist()

res = (
    client.query.get(CLS, ["text","video_id","start","end","source"])
    .with_hybrid(query=q, alpha=0.3, vector=qvec)   # lower alpha = rely more on semantic
    .with_limit(3)
    .with_additional(["score"])
    .do()
)
print(res)
