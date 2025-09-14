\
import os, json, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from qa import answer

TRANSCRIPTS = os.path.join(os.path.dirname(__file__), "..", "transcripts")

def run_case(q: str):
    res = answer(q, TRANSCRIPTS)
    print("Q:", q)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return res

if __name__ == "__main__":
    print("== Mini Evaluation ==")
    # 1) Schema: any reasonable question should have citations
    res1 = run_case("How should I structure the first 30 seconds of my intro?")
    assert res1["citations"], "Schema FAIL: expected at least one citation"

    # 2) Grounding: pacing/storytelling should hit video_2 (Hayden)
    res2 = run_case("Explain pacing and the idea of peaks and valleys in storytelling")
    vids = {c['video'] for c in res2.get("citations", [])}
    assert "video_2" in vids, "Grounding FAIL: expected a citation to video_2"

    # 3) Fallback: out-of-scope
    res3 = run_case("What camera should I buy for vlogging under $500?")
    assert not res3["citations"], "Fallback FAIL: expected no citations for out-of-scope"
    print("All checks passed.")
