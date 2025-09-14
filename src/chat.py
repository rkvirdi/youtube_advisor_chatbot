\
import argparse, json, os, sys
from qa import answer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", required=True, help="Your question")
    parser.add_argument("--transcripts", default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "transcripts"))
    args = parser.parse_args()
    result = answer(args.q, args.transcripts)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # enable relative imports from src
    sys.path.append(os.path.dirname(__file__))
    main()
