import os, weaviate
from sentence_transformers import SentenceTransformer

URL = os.getenv("WEAVIATE_URL", "http://127.0.0.1:8081")
CLS = os.getenv("WEAVIATE_CLASS_NAME", "TranscriptChunk")
MODEL = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

print("URL:", URL, "CLASS:", CLS, "MODEL:", MODEL)
client = weaviate.Client(URL)
model = SentenceTransformer(MODEL)

# Ensure class
if not client.schema.exists(CLS):
    client.schema.create({
        "classes": [{
            "class": CLS,
            "vectorizer": "none",
            "properties": [
                {"name":"text","dataType":["text"]},
                {"name":"video_id","dataType":["text"]},
                {"name":"start","dataType":["text"]},
                {"name":"end","dataType":["text"]},
                {"name":"source","dataType":["text"]},
            ],
        }]
    })

text = "Hook the viewer in the first 5–10 seconds by stating a clear promise, then deliver quickly."
vec = model.encode(text).tolist()
props = {
    "text": text,
    "video_id": "sanity_test",
    "start": "00:00:00.000",
    "end": "00:00:10.000",
    "source": "manual_sanity",
}

# Write one object
uuid = client.data_object.create(props, CLS, vector=vec)
print("Created:", uuid)

# Verify
print("Count after insert:",
      client.query.aggregate(CLS).with_meta_count().do())
print("One object:",
      client.query.get(CLS, ["text","video_id","start","end","source"]).with_limit(1).do())
