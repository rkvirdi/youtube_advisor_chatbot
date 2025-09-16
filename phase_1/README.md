
# YouTube Advisor — CLI & API

This project helps you query YouTube transcript chunks stored in Weaviate and generate concise, cited answers. You can use it via:

- **CLI:** `src/main.py`
- **HTTP API:** FastAPI (`src/routes/ask.py`)

Both paths reuse the same retriever and generator logic.

---

## 1. Requirements

- Python 3.10+
- Docker Desktop (to run Weaviate locally)
- (Optional) Groq API key — for LLM summaries

---

## 2. Quick Start

### 2.1 Run Weaviate (local)

This project needs a running Weaviate server. Start it with Docker:

```bash
docker run -d --name weaviate \
  -p 8081:8080 \
  semitechnologies/weaviate:1.25.7
```

#### Check if it’s ready

```bash
curl http://127.0.0.1:8081/v1/.well-known/ready
```

You should see: `{"status":"READY"}`.

### 2.2 Create your .env

k — how many candidates to pull from Weaviate (default 30)

Create a `.env` file in the repo root:

```env
# Weaviate
WEAVIATE_URL=http://127.0.0.1:8081
WEAVIATE_CLASS_NAME=TranscriptChunk
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# (Optional) Groq LLM — for nicer answers
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Without `GROQ_API_KEY`, the app falls back to a fast extractive (no-LLM) summarizer.

### 2.3 Install dependencies

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, minimally:

```bash
pip install weaviate-client sentence-transformers fastapi uvicorn python-dotenv groq
```

---

## 3. Ingest your transcripts

Put your transcript files under:

```
phase_1/transcripts/
```

Run ingestion:

```bash
python -m scripts.ingestion_script
```

Expected output (example):

```
[ingest] looking in: .../phase_1/transcripts
[ingest] loaded docs: 2858
[embed] URL=http://127.0.0.1:8081 CLASS=TranscriptChunk MODEL=sentence-transformers/all-MiniLM-L6-v2
[embed] incoming docs: 2858
[embed] count BEFORE: {... "count": 0}
[embed] attempted writes: 2858
[embed] count AFTER: {... "count": 2858}
```

Verify:

```bash
python -m scripts.debug_weaviate
# Expect: Count > 0 and one sample object
```

---

## 4. Use the CLI

Ask a question in the terminal:

```bash
python -m src.main
# Ask your question: How can I improve my thumbnails and CTR?
```

If `GROQ_API_KEY` is set: you’ll get 3 clean bullets with citations.

If not: you’ll get an extractive summary with citations.

---

## 5. Run the HTTP API (FastAPI)

Start the server:

```bash
uvicorn src.routes.ask:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

Ask a question:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"How can I improve my thumbnails and CTR?","k":30,"alpha":0.15}'
```

Response shape:

```json
{
  "answer": "- Use bold, high-contrast faces ... [source: video_1 ...]\n- ...",
  "retrieved": 30
}
```

**Parameters:**

- `k` — how many candidates to pull from Weaviate (default 30)
- `alpha` — BM25 vs vector blend (0 = semantic-heavy; 1 = keyword-only). Try 0.1–0.3 for best results with semantic retrieval.

---

## Project Structure (simplified)

```text
phase_1/
  scripts/
    ingestion_script.py        # loads transcripts -> embed_and_store
  src/
    main.py                   # CLI runner
    routes/
      ask.py                  # FastAPI app
    utils/
      retriever.py            # hybrid retrieval (BM25 + vector)
      generator.py            # Groq summary or extractive fallback
      embed.py                # embed & store
      chunk.py                # transcript parsing/chunking
  transcripts/                # your .vtt/.txt transcript files
  .env                        # environment variables
  requirements.txt
```

---

## Example Prompts

- How can I improve my thumbnails and CTR?
- What should I say in the first 10 seconds to hook viewers?
- How should title and thumbnail work together?
- Common intro mistakes that kill retention?