# src/qa.py
from typing import List, Dict
import regex as re
import os
from index import load_corpus, build_index, search

ADVICE_VERBS = (
    "keep","avoid","match","write","provide","create","show","measure","use",
    "focus","shorten","mention","respect","set","test","explain","introduce",
    "hook","structure","pace","build","raise","lower","tease","withhold",
    "deliver","promise","title","thumbnail","curiosity","edit","cut","trim",
    "reveal","withhold","foreshadow","frame","open","start","end","close"
)

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Explicitly out-of-scope (buying gear / prices etc.)
OUT_OF_SCOPE_RE = re.compile(
    r"(camera|mirrorless|dslr|lens|sensor|sony|canon|nikon|gopro|"
    r"microphone|mic|lighting|light kit|tripod|gimbal|stabilizer|"
    r"\$\s*\d+|under\s*\$?\s*\d+|\d+\s*(usd|dollars))",
    re.I
)

def _pick_actionable_sentence(text: str) -> str:
    sentences = SENT_SPLIT.split(text)
    for s in sentences:
        low = s.lower()
        if any(v in low for v in ADVICE_VERBS) and 6 <= len(s.split()) <= 45:
            return s.strip()
    sentences = sorted(sentences, key=lambda s: -len(s))
    return sentences[0].strip() if sentences else text.strip()

def _fmt_ts(ts: str) -> str:
    return ts.split(".")[0]

def _fallback_msg() -> Dict:
    return {
        "answer": ["Sorry — the transcripts don’t cover equipment buying or pricing. Ask about intros or storytelling (hooks, pacing, structure) and I’ll cite exact timestamps."],
        "citations": []
    }

def answer(question: str, transcripts_dir: str | None = None, k: int = 5) -> Dict:
    """
    Answer a question grounded ONLY in the provided transcripts.
    """
    # 1) Hard out-of-scope filter (gear/price)
    if OUT_OF_SCOPE_RE.search(question or ""):
        return _fallback_msg()

    # 2) Load & search
    if transcripts_dir is None:
        transcripts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "transcripts")
        )
    segs = load_corpus(transcripts_dir)
    idx = build_index(segs)
    hits = search(idx, question, top_k=k)

    # 3) Similarity floor to avoid spurious matches
    if not hits or hits[0][1] < 0.05:  # cosine sim threshold
        return {
            "answer": ["I couldn’t find a strong match in the transcripts. Try rephrasing toward intros/storytelling craft."],
            "citations": []
        }

    bullets: List[str] = []
    cites: List[Dict] = []
    used = set()
    for seg, score in hits:
        key = (seg.video_id, seg.start, seg.end)
        if key in used:
            continue
        used.add(key)
        rec = _pick_actionable_sentence(seg.text)
        if not rec:
            continue
        t_s, t_e = _fmt_ts(seg.start), _fmt_ts(seg.end)
        bullets.append(f"- {rec} [source: {seg.video_id} t={t_s}–{t_e}]")
        cites.append({"video": seg.video_id, "t_start": t_s, "t_end": t_e})

    if not bullets:
        return {
            "answer": ["Sorry — I couldn’t extract actionable lines for this question, but the transcripts may still be relevant."],
            "citations": []
        }

    return {"answer": bullets, "citations": cites}
