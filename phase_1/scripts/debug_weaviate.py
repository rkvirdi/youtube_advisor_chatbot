# scripts/debug_weaviate.py
import os, weaviate
URL = os.getenv("WEAVIATE_URL", "http://127.0.0.1:8081")
CLS = os.getenv("WEAVIATE_CLASS_NAME", "TranscriptChunk")
c = weaviate.Client(URL)

print("Count:", c.query.aggregate(CLS).with_meta_count().do())
print("One:", c.query.get(CLS, ["text","video_id","start","end","source"]).with_limit(1).do())
