from src.utils.chunk import Chunks
from src.utils.embed import embed_and_store

transcripts_dir = 'phase_1/transcripts'

documents = Chunks.parse_all_webvtt_in_dir(transcripts_dir)

# print(f"Loaded {len(documents)} timestamped chunks from {transcripts_dir}")

# for i, doc in enumerate(documents):
#     print(f"\nChunk {i+1}:")
#     print("Metadata:", doc.metadata)
#     print("Context snippet:", doc.page_content[:200], "...")

# Embed and store in Weaviate
embed_and_store(documents)