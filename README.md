# Transcript_Grounded_YouTube_Advisor

A tiny, production‑minded chatbot that gives **actionable YouTube advice** grounded **only** in two provided video transcripts.  
Every recommendation includes a **machine‑checkable citation** to a transcript file and **timestamp range**.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

No external APIs or keys required.

## Run (CLI)

```bash
python src/chat.py --q "How do I write a killer intro?"
```

Example output (shape):
```json
{
  "answer": [
    "- Match your very first sentence to the promise in the title/thumbnail to confirm expectations. [source: video_1 t=00:06:31–00:06:40]",
    "- Keep intros short (≈20–40s, ~5–7 sentences) to respect attention. [source: video_1 t=00:22:36–00:23:09]"
  ],
  "citations": [
    {"video":"video_1","t_start":"00:06:31","t_end":"00:06:40"},
    {"video":"video_1","t_start":"00:22:36","t_end":"00:23:09"}
  ]
}
```

## Tests

```bash
python -m pytest -q
```
(Uses standard `unittest` runner via `python tests/test_eval.py` if `pytest` not installed.)

Or run the mini harness:
```bash
python tests/eval.py
```

## Model/Library Choices
- **TF‑IDF (scikit‑learn)** for fast, deterministic retrieval.
- No LLM calls by default for reproducibility and zero cost.

## Limits
- Advice is limited to what exists in the two transcripts.
- Lexical retrieval may miss deeply paraphrased ideas.
- Heuristic extraction may include some non‑imperative lines; still correctly cited.

## Future Improvements
- Swap to BM25 or local sentence embeddings for better recall.
- Add FastAPI `POST /ask` endpoint with streaming responses.
- More robust sentence ranking for “actionability.”
