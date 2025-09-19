# YouTube Advisor — Design Overview

## Purpose

Enable creators to query YouTube video transcripts and get concise, cited answers to content strategy questions.

## Architecture

- **Transcript Ingestion Pipeline**
  - Loads transcript files (.txt/.vtt)
  - Chunks into timestamped passages
  - Embeds with SentenceTransformer
  - Stores in Weaviate with metadata (video, start/end time)

- **Retrieval & Generation Pipeline**
  - Accepts user query (CLI/API)
  - Hybrid retrieval: BM25 + semantic vector search
  - Returns top-k relevant transcript chunks
  - Generates answer (extractive bullets or LLM summary)
  - Formats citations: `[source: video_1 t=00:12:34–00:13:10]`

- **API Layer**
  - FastAPI app for HTTP queries
  - Health check and `/ask` endpoint

## Key Modules

- [ingestion_script.py](http://_vscodecontentref_/10): Orchestrates loading, chunking, embedding, and storing transcripts.
- [retriever.py](http://_vscodecontentref_/11): Hybrid retrieval from Weaviate.
- [generator.py](http://_vscodecontentref_/12): Generates answers with citations; uses Groq LLM if available.
- [embed.py](http://_vscodecontentref_/13): Handles embedding and batch storage.
- [chunk.py](http://_vscodecontentref_/14)/[preprocessor.py](http://_vscodecontentref_/15): Parses and chunks transcripts.
- [main.py](http://_vscodecontentref_/16): CLI entry point.
- [ask.py](http://_vscodecontentref_/17): FastAPI app.

## Data Flow

1. **Ingestion:** Transcript files → chunked → embedded → stored in Weaviate.
2. **Query:** User question → retrieval (BM25 + semantic) → top chunks → answer generation → citations.

## Extensibility

- Add new transcript files and re-run ingestion.
- Swap embedding models or LLMs via `.env`.
- Extend API endpoints for more features.

## Testing

- Pytest suite covers fallback, grounding, integration, and schema.
- Tests ensure citations, retrieval, and answer formatting are correct.

## Citation Format

All answers cite sources in a machine-checkable format:

[source: video_1 t=00:12:34–00:13:10]


## Example Use Cases

- Content strategy Q&A for creators
- Automated video analysis
- Research on YouTube best practices

