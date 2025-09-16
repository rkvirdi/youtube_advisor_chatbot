
import re
from pathlib import Path
from langchain_core.documents import Document

class PreprocessData:
	@staticmethod
	def parse_webvtt_transcript(file_path, video_id=None):
		"""
		Parse a WEBVTT transcript file and return a list of LangChain Document objects,
		each with text and metadata (video_id, start, end).
		"""
		time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})")
		docs = []
		with open(file_path, 'r', encoding='utf-8') as f:
			content = f.read()
		# Remove WEBVTT header if present
		content = re.sub(r"^WEBVTT\s*", "", content)
		for match in re.finditer(r"(\d+)\n([\d:,\.\-\>\s]+)\n([\s\S]*?)(?=\n\d+\n|\Z)", content):
			idx = match.group(1)
			times = match.group(2)
			text = match.group(3).strip()
			time_match = time_pattern.search(times)
			if not time_match:
				continue
			start, end = time_match.group(1), time_match.group(2)
			doc = Document(
				page_content=text,
				metadata={
					"video_id": video_id or Path(file_path).stem,
					"start": start,
					"end": end,
					"source": str(file_path)
				}
			)
			docs.append(doc)
		return docs

# if __name__ == "__main__":
#  # Resolve transcripts dir relative to THIS file: phase_1/transcripts
#     project_root = Path(__file__).resolve().parents[2]  # .../phase_1
#     transcripts_dir = project_root / "transcripts"

#     folder = Path(transcripts_dir)
#     all_docs = []

#     for file_path in folder.glob("*.txt"):
#         all_docs.extend(PreprocessData.parse_webvtt_transcript(file_path))

#     if all_docs:
#         print(all_docs[0])
#     else:
#         print("No cues parsed. Check file patterns or transcript format.")