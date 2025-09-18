#!/usr/bin/env python3
# Rule-based judge only: scores 1–5 for helpfulness, groundedness, relevance.
# No external deps.

import argparse, json, re, statistics as stats
from pathlib import Path

def load_rows(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Predictions file not found: {path}")
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported JSON structure in: {path}")

def toks(s: str): return set((s or "").lower().split())
def contains_cite(ans: str) -> bool:
    # looks for [source: ...] / [ref: ...] or timestamp-like t=MM:SS
    return bool(re.search(r"\[(source|ref)\s*:\s*.+?\]", ans or "", re.I)) or bool(re.search(r"t=\d{1,2}:\d{2}", ans or ""))

def overlap(a: str, b: str) -> float:
    A, B = toks(a), toks(b)
    return (len(A & B) / max(1, len(B))) if A and B else 0.0

def score_item(q: str, a: str, ref: str, ctxs):
    # Helpfulness: prefer overlap with reference; fall back to contexts
    if ref:
        helpful = round(5 * overlap(a, ref))
    else:
        helpful = round(5 * min(1.0, overlap(a, " ".join(ctxs or [])) * 1.2))

    # Groundedness: context overlap + citation presence bonus
    grounded = round(5 * min(1.0, (overlap(a, " ".join(ctxs or [])) * 0.7 + (0.3 if contains_cite(a) else 0.0))))

    # Relevance: answer vs question
    relevance = round(5 * overlap(a, q)) if q else 3

    clamp = lambda x: max(1, min(5, int(x)))
    return {
        "helpfulness": clamp(helpful),
        "groundedness": clamp(grounded),
        "relevance": clamp(relevance),
        "comments": ""
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    rows = load_rows(args.predictions)
    items = []
    for r in rows:
        q = r.get("question",""); a = r.get("prediction",""); ref = r.get("reference","")
        ctx = r.get("retrieved_contexts") or []
        items.append({"id": r.get("id"), "judge": score_item(q,a,ref,ctx)})

    mean = {
        "helpfulness": stats.fmean(i["judge"]["helpfulness"] for i in items) if items else 0.0,
        "groundedness": stats.fmean(i["judge"]["groundedness"] for i in items) if items else 0.0,
        "relevance": stats.fmean(i["judge"]["relevance"] for i in items) if items else 0.0,
    }
    report = {"meta": {"total": len(items)}, "mean": mean, "items": items}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved judge report -> {args.output}")

if __name__ == "__main__":
    main()
