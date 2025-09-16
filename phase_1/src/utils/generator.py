# src/utils/generator.py
import os, re
from typing import List, Dict

# ---------- Fallback (extractive bullets, no LLM) ----------
KW = {
    "thumbnail","thumbnails","ctr","click-through","click through",
    "title","titles","contrast","high-contrast","face","faces",
    "focal point","text size","tiny text","test","a/b","poll","variant",
    "complementary","redundant","split-testing","split testing"
}

def _sents(t: str):
    parts = re.split(r'(?<=[.!?])\s+', (t or "").strip())
    return [p.strip() for p in parts if p.strip()]

def _score(sent: str, query: str):
    s = sent.lower(); q = query.lower()
    kw_hits = sum(1 for k in KW if k in s)
    q_hits  = sum(1 for w in re.findall(r"[a-z0-9]+", q) if w in s)
    return kw_hits*3 + q_hits

def _clean(s: str):
    s = re.sub(r'^\W+', '', s).strip()
    if s and s[-1] not in ".!?": s += "."
    return s[0].upper()+s[1:] if s else s

def _extractive_bullets(user_query: str, chunks: List[Dict], bullets: int = 3) -> str:
    if not chunks:
        return "No relevant information found in the transcripts. Please clarify your question."
    cand = []
    for c in chunks:
        cite = f"[source: {c.get('video_id','?')} t={c.get('start','?')}–{c.get('end','?')}]"
        for s in _sents(c.get("text","")):
            sc = _score(s, user_query)
            if sc > 0:
                cand.append((sc, s, cite))
    if not cand:
        for c in chunks[:bullets*3]:
            sents = _sents(c.get("text",""))
            if sents:
                cite = f"[source: {c.get('video_id','?')} t={c.get('start','?')}–{c.get('end','?')}]"
                cand.append((1, sents[0], cite))
    cand.sort(key=lambda x: x[0], reverse=True)
    out, used = [], set()
    for _, s, cite in cand:
        line = _clean(s)
        sig = (line, cite)
        if sig in used or not line: 
            continue
        out.append(f"- {line} {cite}")
        used.add(sig)
        if len(out) >= bullets:
            break
    return "\n".join(out) if out else "No relevant information found in the transcripts. Please clarify your question."

# ---------- Groq LLM mode ----------
_USE_GROQ = False
try:
    if os.getenv("GROQ_API_KEY"):
        from groq import Groq
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        _USE_GROQ = True
except Exception:
    _USE_GROQ = False

_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # fast/strong default

def _format_ctx(chunks: List[Dict]) -> str:
    lines = []
    for c in chunks:
        cite = f"[source: {c.get('video_id','?')} t={c.get('start','?')}–{c.get('end','?')}]"
        txt = (c.get("text","") or "").strip().replace("\n", " ")
        if txt:
            lines.append(f"- {txt}\n  {cite}")
    return "\n".join(lines[:20])  # keep prompt compact

def _groq_answer(user_query: str, chunks: List[Dict]) -> str:
    if not chunks:
        return "No relevant information found in the transcripts. Please clarify your question."
    system = (
        "You are a YouTube growth coach. Using ONLY the provided transcript excerpts, "
        "write 3 concise, actionable bullets about thumbnails/CTR or the asked topic. "
        "Each bullet MUST end with one or more bracketed citations in the format "
        "[source: <video_id> t=<start>–<end>]. If the excerpts don't contain the answer, say so."
    )
    user = (
        f"Question: {user_query}\n\n"
        f"Excerpts (each line ends with a citation you must preserve at the end of the bullet it supports):\n"
        f"{_format_ctx(chunks)}\n\n"
        "Output exactly 3 bullets. No preamble, no conclusion."
    )
    try:
        resp = _groq_client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_completion_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        # graceful fallback
        return _extractive_bullets(user_query, chunks, bullets=3)

def generate_response(user_query: str, retrieved_chunks: List[Dict]) -> str:
    if _USE_GROQ:
        return _groq_answer(user_query, retrieved_chunks)
    return _extractive_bullets(user_query, retrieved_chunks, bullets=3)


# def generate_response(user_query, retrieved_chunks):
# 	"""
# 	Generate a response using retrieved transcript chunks, including citations.
# 	retrieved_chunks: list of dicts with keys 'text', 'video_id', 'start', 'end', 'source'
# 	"""
# 	if not retrieved_chunks:
# 		return "No relevant information found in the transcripts. Please clarify your question."

# 	response_parts = []
# 	citations = []
# 	for chunk in retrieved_chunks:
# 		# Add chunk text to response
# 		response_parts.append(chunk['text'])
# 		# Format citation
# 		citations.append(f"[source: {chunk['video_id']} t={chunk['start']}–{chunk['end']}]")

# 	response_text = "\n---\n".join(response_parts)
# 	citation_text = "\n".join(citations)

# 	return f"Answer based on retrieved transcript chunks:\n\n{response_text}\n\nCitations:\n{citation_text}"
