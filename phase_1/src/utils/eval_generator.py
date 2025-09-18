from __future__ import annotations
import argparse, json, math, statistics as stats
from pathlib import Path
from typing import Dict, List

def _read_jsonl(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def _write_json(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def _tokenize(s: str) -> List[str]:
    return s.lower().strip().split()

def exact_match(pred: str, ref: str) -> bool:
    return pred.strip().lower() == ref.strip().lower()

def bleu4(pred: str, ref: str) -> float:
    try:
        import nltk
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    except Exception:
        # Light-weight 0..1 fallback: unigram precision * brevity penalty
        p_tok, r_tok = _tokenize(pred), _tokenize(ref)
        if not p_tok: return 0.0
        hits = sum(1 for t in p_tok if t in set(r_tok))
        prec = hits / len(p_tok)
        bp = math.exp(1 - len(r_tok)/len(p_tok)) if len(p_tok) < len(r_tok) and len(p_tok)>0 else 1.0
        return float(prec * bp)

    nltk.download('punkt', quiet=True)
    smoothie = SmoothingFunction().method3
    return float(sentence_bleu([_tokenize(ref)], _tokenize(pred), smoothing_function=smoothie))

def rouge_l(pred: str, ref: str) -> float:
    # Simple LCS-based F1
    a, b = _tokenize(pred), _tokenize(ref)
    if not a or not b: return 0.0
    # DP LCS
    dp = [[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            dp[i][j] = dp[i-1][j-1]+1 if a[i-1]==b[j-1] else max(dp[i-1][j], dp[i][j-1])
    lcs = dp[-1][-1]
    prec = lcs/len(a)
    rec  = lcs/len(b)
    if prec+rec==0: return 0.0
    return float(2*prec*rec/(prec+rec))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    rows = _read_jsonl(args.predictions)
    metrics = []
    for r in rows:
        pred, ref = r.get("prediction",""), r.get("reference","")
        item = {
            "id": r.get("id"),
            "exact_match": exact_match(pred, ref),
            "bleu4": bleu4(pred, ref),
            "rougeL": rouge_l(pred, ref),
            "len_pred": len(_tokenize(pred)),
            "len_ref":  len(_tokenize(ref)),
        }
        metrics.append(item)

    report = {
        "meta": {"total": len(metrics)},
        "mean": {
            "exact_match": sum(1 for m in metrics if m["exact_match"])/len(metrics) if metrics else 0.0,
            "bleu4": stats.fmean(m["bleu4"] for m in metrics) if metrics else 0.0,
            "rougeL": stats.fmean(m["rougeL"] for m in metrics) if metrics else 0.0,
            "len_pred": stats.fmean(m["len_pred"] for m in metrics) if metrics else 0.0,
            "len_ref":  stats.fmean(m["len_ref"] for m in metrics) if metrics else 0.0,
        },
        "items": metrics
    }
    _write_json(args.output, report)
    print(f"Saved generator metrics -> {args.output}")


if __name__ == "__main__":
    main()