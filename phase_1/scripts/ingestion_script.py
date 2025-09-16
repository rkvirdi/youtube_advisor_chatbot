# scripts/ingestion_script.py
from pathlib import Path
from src.utils.chunk import Chunks
from src.utils.embed import embed_and_store

BASE_DIR = Path(__file__).resolve().parents[1]      # -> .../phase_1
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"          # -> .../phase_1/transcripts

print("[ingest] looking in:", TRANSCRIPTS_DIR)

documents = Chunks.parse_all_webvtt_in_dir(str(TRANSCRIPTS_DIR))

print("[ingest] loaded docs:", len(documents))
if not documents:
    print("[ingest] files in dir:", [p.name for p in TRANSCRIPTS_DIR.glob("*")][:20])
    raise SystemExit("[ingest] 0 docs loaded. Likely wrong path or file extensions (.vtt vs .txt).")

# Write to Weaviate
embed_and_store(documents)


# from src.utils.chunk import Chunks
# from src.utils.embed import embed_and_store

# transcripts_dir = 'phase_1/transcripts'

# documents = Chunks.parse_all_webvtt_in_dir(transcripts_dir)

# # print(f"Loaded {len(documents)} timestamped chunks from {transcripts_dir}")

# # for i, doc in enumerate(documents):
# #     print(f"\nChunk {i+1}:")
# #     print("Metadata:", doc.metadata)
# #     print("Context snippet:", doc.page_content[:200], "...")

# # Embed and store in Weaviate
# embed_and_store(documents)