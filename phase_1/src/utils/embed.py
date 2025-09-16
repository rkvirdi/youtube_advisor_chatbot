from sentence_transformers import SentenceTransformer
import weaviate, os

def embed_and_store(docs, weaviate_url=None, class_name=None, model_name=None):
    weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL", "http://127.0.0.1:8081")
    class_name   = class_name   or os.getenv("WEAVIATE_CLASS_NAME", "TranscriptChunk")
    model_name   = model_name   or os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

    print(f"[embed] URL={weaviate_url} CLASS={class_name} MODEL={model_name}")
    print(f"[embed] incoming docs: {len(docs)}")
    if not docs:
        raise ValueError("[embed] No docs to ingest. Check your loader/path.")

    model = SentenceTransformer(model_name)
    client = weaviate.Client(weaviate_url)

    # Ensure class
    if not client.schema.exists(class_name):
        client.schema.create({
            "classes": [{
                "class": class_name,
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

    # Count before
    before = client.query.aggregate(class_name).with_meta_count().do()
    print("[embed] count BEFORE:", before)

    # Capture batch errors
    def _cb(results):
        for r in results:
            if not r.get("success", True):
                print("BATCH ERROR:", r.get("err"))

    client.batch.configure(batch_size=64, callback=_cb)

    wrote = 0
    with client.batch as batch:
        for i, doc in enumerate(docs):
            text = getattr(doc, "page_content", "") or ""
            if not text.strip():
                continue
            vec = model.encode(text).tolist()
            meta = (getattr(doc, "metadata", None) or {})
            props = {
                "text": text,
                "video_id": meta.get("video_id",""),
                "start": meta.get("start",""),
                "end": meta.get("end",""),
                "source": meta.get("source",""),
            }
            batch.add_data_object(props, class_name=class_name, vector=vec)
            wrote += 1

    print(f"[embed] attempted writes: {wrote}")

    # Count after
    after = client.query.aggregate(class_name).with_meta_count().do()
    print("[embed] count AFTER:", after)


# from sentence_transformers import SentenceTransformer
# import weaviate
# import os

# def embed_and_store(
#     docs,
#     weaviate_url=None,
#     class_name=None,
#     model_name=None
# ):
#     weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL", "http://127.0.0.1:8081")  
#     class_name   = class_name   or os.getenv("WEAVIATE_CLASS_NAME", "TranscriptChunk")
#     model_name   = model_name   or os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

#     if not weaviate_url:
#         raise ValueError("WEAVIATE_URL is not set. Provide weaviate_url or set the env var.")

#     # Load embedding model
#     model = SentenceTransformer(model_name)

#     client = weaviate.Client(weaviate_url)
#     print(client.schema.get())   # should return {}



#     # Ensure class exists
#     if not client.schema.exists(class_name):
#         schema = {
#             "classes": [
#                 {
#                     "class": class_name,
#                     "vectorizer": "none",
#                     "properties": [
#                         {"name": "text", "dataType": ["text"]},
#                         {"name": "video_id", "dataType": ["text"]},
#                         {"name": "start", "dataType": ["text"]},
#                         {"name": "end", "dataType": ["text"]},
#                         {"name": "source", "dataType": ["text"]},
#                     ],
#                 }
#             ]
#         }
#         client.schema.create(schema)

#     # (Optional) Faster writes via batch
#     with client.batch as batch:
#         batch.batch_size = 64
#         for doc in docs:
#             text = doc.page_content
#             vec = model.encode(text).tolist()
#             meta = doc.metadata or {}
#             props = {
#                 "text": text,
#                 "video_id": meta.get("video_id", ""),
#                 "start": meta.get("start", ""),
#                 "end": meta.get("end", ""),
#                 "source": meta.get("source", ""),
#             }
#             batch.add_data_object(props, class_name=class_name, vector=vec)
