#!/usr/bin/env python3
"""
Evaluation orchestrator for a RAG pipeline.

This script:
1) Runs generator metrics (EM, BLEU-4, ROUGE-L)
2) Runs BERTScore
3) Runs Judge (HF-only by default; rule-based if model is empty)
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
from typing import Dict

def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("---- CMD ----\n" + " ".join(cmd), file=sys.stderr)
        print("---- STDOUT ----\n" + (p.stdout or ""), file=sys.stderr)
        print("---- STDERR ----\n" + (p.stderr or ""), file=sys.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return p

def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def _write_json(path: Path, obj: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)

    # BERTScore settings
    ap.add_argument("--bertscore_model", default=None, help="e.g., roberta-large or microsoft/deberta-xlarge-mnli")
    ap.add_argument("--lang", default="en", help="BERTScore language if model is not provided")


    args = ap.parse_args()

    # Resolve absolute paths for everything
    here = Path(__file__).parent.resolve()  # .../phase_1/src/utils
    gen_py   = (here / "eval_generator.py").resolve()
    bert_py  = (here / "eval_bertscore.py").resolve()
    judge_py = (here / "eval_judge.py").resolve()
    pred_path = args.predictions.resolve()
    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) Generator metrics
    gen_json = outdir / "generator.json"
    _run([sys.executable, str(gen_py),
          "--predictions", str(pred_path),
          "--output", str(gen_json)])

    # 2) BERTScore
    bert_json = outdir / "bertscore.json"
    cmd = [sys.executable, str(bert_py),
           "--predictions", str(pred_path),
           "--output", str(bert_json),
           "--lang", args.lang]
    if args.bertscore_model:
        cmd += ["--model_type", args.bertscore_model]
    _run(cmd)

   # 3) Judge (rule-based only)
    judge_json = outdir / "judge.json"
    judge_cmd = [sys.executable, str(judge_py),
             "--predictions", str(pred_path),
             "--output", str(judge_json)]
    _run(judge_cmd)


    # Combine summaries
    gen = _read_json(gen_json)
    bert = _read_json(bert_json)
    judge = _read_json(judge_json)

    combined = {
        "meta": {"total": gen["meta"]["total"]},
        "macro": {
            "exact_match": gen["mean"]["exact_match"],
            "bleu4": gen["mean"]["bleu4"],
            "rougeL": gen["mean"]["rougeL"],
            "bertscore_f1": bert["mean"]["f1"],
            "bertscore_precision": bert["mean"]["precision"],
            "bertscore_recall": bert["mean"]["recall"],
            "judge_helpfulness": judge["mean"]["helpfulness"],
            "judge_groundedness": judge["mean"]["groundedness"],
            "judge_relevance": judge["mean"]["relevance"],
        },
        "paths": {
            "generator": str(gen_json),
            "bertscore": str(bert_json),
            "judge": str(judge_json),
        }
    }
    _write_json(outdir / "summary.json", combined)
    print(f"Done. Summary -> {outdir / 'summary.json'}")


if __name__ == "__main__":
    main()
