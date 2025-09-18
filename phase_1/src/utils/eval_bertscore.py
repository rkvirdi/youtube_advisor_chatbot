from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import List, Dict

def _read_jsonl(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def _write_json(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def compute_bertscore(preds: List[str], refs: List[str], lang: str = "en", model_type: str | None = None):
    try:
        from bert_score import score as bertscore_score
    except Exception as e:
        raise RuntimeError(
            "bert-score is not installed. Install with: pip install bert-score"
        ) from e

    # If model_type is provided, bert-score ignores lang.
    P, R, F1 = bertscore_score(preds, refs, lang=None if model_type else lang, model_type=model_type, verbose=True)
    return {
        "precision": [float(x) for x in P],
        "recall":    [float(x) for x in R],
        "f1":        [float(x) for x in F1],
        "mean": {
            "precision": float(P.mean().item()),
            "recall":    float(R.mean().item()),
            "f1":        float(F1.mean().item())
        }
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True, type=Path, help="JSONL file with prediction/reference")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--model_type", default=None, help="e.g. roberta-large, microsoft/deberta-xlarge-mnli")
    args = ap.parse_args()

    rows = _read_jsonl(args.predictions)
    preds = [r.get("prediction", "") for r in rows]
    refs  = [r.get("reference", "") for r in rows]

    if not preds or not refs or len(preds) != len(refs):
        print("Error: predictions and references must be non-empty and same length.", file=sys.stderr)
        sys.exit(2)

    result = compute_bertscore(preds, refs, lang=args.lang, model_type=args.model_type)
    # attach per-id
    per_item = []
    for r, p, ref, pr, rc, f1 in zip(rows, preds, refs, result["precision"], result["recall"], result["f1"]):
        per_item.append({
            "id": r.get("id"),
            "prediction": p,
            "reference": ref,
            "bertscore": {"precision": pr, "recall": rc, "f1": f1}
        })

    report = {"meta": {"total": len(rows)}, "mean": result["mean"], "items": per_item}
    _write_json(args.output, report)
    print(f"Saved BERTScore report -> {args.output}")

if __name__ == "__main__":
    main()