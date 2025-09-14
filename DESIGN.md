# DESIGN

## Goals
- Provide a small, reproducible chatbot that returns **actionable, transcript‑grounded** advice with **precise citations** to file and timestamp ranges.
- No external APIs are required; retrieval and answer composition are done locally for determinism and zero cost.

## Architecture
- **Parser (`parse_vtt.py`)**: Normalizes each transcript (WEBVTT‑like) into timestamped segments: `(video_id, start, end, text)`.
- **Indexer (`index.py`)**: Builds a TF‑IDF vector index over segments for lightweight semantic retrieval.
- **QA (`qa.py`)**: Given a question, retrieves top‑K relevant segments across both videos, extracts **actionable statements**, and formats a response with citations like:
  - `[source: video_1 t=00:12:34–00:13:10]`

### Why TF‑IDF
- Deterministic, fast, and inexpensive. Works well on small corpora (two 1‑hour transcripts).
- Avoids LLM cost/variance while meeting **grounding** requirements.

### Actionability Heuristic
- We scan retrieved segments and pick sentences that look like advice (contain verbs like *keep, avoid, match, write, test, provide, create, show, measure, use, focus, shorten*).
- If none match, we fallback to the highest‑scoring sentence in the segment.
- We keep **verbatim** phrasing when possible for grounding clarity (light trims only).

### Citations
- Each bullet includes the exact file id and **start–end** timestamps of the segment from which it is derived.
- Multiple bullets → multiple citations.

### Interface
- **CLI** via `chat.py`:
  ```bash
  python chat.py --q "How do I improve my video intros?"
  ```
  Prints a JSON object with `answer` and `citations`.

### Tests
- `tests/test_eval.py` runs three lightweight checks:
  1) **Schema**: every answer includes at least one citation in the agreed format.
  2) **Grounding**: a pacing/story question should cite **video_2** (Hayden).
  3) **Fallback**: out‑of‑scope questions elicit a graceful message.

## Tradeoffs & Future Work
- TF‑IDF is lexical; nuanced queries may under‑retrieve. Could swap to **BM25** or small local embeddings.
- The actionability heuristic is simple. Could add pattern libraries per topic (intros vs storytelling).
- A tiny FastAPI endpoint could be added; CLI kept for minimalism & zero deps beyond core libs.
