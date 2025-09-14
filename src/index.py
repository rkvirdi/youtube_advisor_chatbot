\
from typing import List, Dict, Tuple
from dataclasses import dataclass
from parse_vtt import Segment, parse_segments
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

@dataclass
class CorpusIndex:
    vectorizer: TfidfVectorizer
    matrix: any
    segments: List[Segment]

def load_corpus(transcripts_dir: str) -> List[Segment]:
    paths = {
        "video_1": os.path.join(transcripts_dir, "video_1_transcript.txt"),
        "video_2": os.path.join(transcripts_dir, "video_2_transcript.txt"),
    }
    all_segments: List[Segment] = []
    for vid, p in paths.items():
        all_segments.extend(parse_segments(p, vid))
    return all_segments

def build_index(segments: List[Segment]) -> CorpusIndex:
    texts = [s.text for s in segments]
    vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1, max_df=0.9)
    matrix = vectorizer.fit_transform(texts)
    return CorpusIndex(vectorizer=vectorizer, matrix=matrix, segments=segments)

def search(index: CorpusIndex, query: str, top_k: int = 6) -> List[Tuple[Segment, float]]:
    q_vec = index.vectorizer.transform([query])
    sims = cosine_similarity(q_vec, index.matrix).ravel()
    top_idx = sims.argsort()[::-1][:top_k]
    return [(index.segments[i], float(sims[i])) for i in top_idx if sims[i] > 0.0]
