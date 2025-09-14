\
import regex as re
from dataclasses import dataclass
from typing import List, Tuple

TIMECODE_RE = re.compile(r"(?P<start>\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2}\.\d{3})")

@dataclass
class Segment:
    video_id: str            # "video_1" or "video_2"
    start: str               # "HH:MM:SS.mmm"
    end: str                 # "HH:MM:SS.mmm"
    text: str

def _load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def parse_segments(path: str, video_id: str) -> List[Segment]:
    """
    Parse a WEBVTT-like transcript into timestamped segments.
    We treat each timecode block as one segment by concatenating the following text lines
    until the next timecode.
    """
    raw = _load_text(path)
    lines = raw.splitlines()
    segments: List[Segment] = []
    i = 0
    current = None
    buffer = []

    def flush():
        nonlocal current, buffer
        if current is not None:
            text = " ".join([t.strip() for t in buffer if t.strip() and not t.strip().isdigit()])
            # Remove residual time-like noise inside text line numbers
            text = re.sub(r"\s+", " ", text).strip()
            segments.append(Segment(video_id=video_id, start=current[0], end=current[1], text=text))
        current = None
        buffer = []

    while i < len(lines):
        line = lines[i]
        m = TIMECODE_RE.search(line)
        if m:
            # starting a new segment
            flush()
            current = (m.group("start")[:12], m.group("end")[:12])  # keep HH:MM:SS.mmm
            buffer = []
        else:
            if current is not None:
                buffer.append(line)
        i += 1
    flush()
    # Filter out empty text segments
    segments = [s for s in segments if s.text]
    return segments
