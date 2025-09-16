from pathlib import Path
from .preprocessor import PreprocessData

class Chunks:
	@staticmethod
	def parse_all_webvtt_in_dir(transcripts_dir):
		"""
		Parse all .txt files in a directory as WEBVTT transcripts.
		Returns a list of Document objects.
		"""
		all_docs = []
		for file_path in Path(transcripts_dir).glob('*.txt'):
			docs = PreprocessData.parse_webvtt_transcript(file_path)
			all_docs.extend(docs)
		return all_docs
	
# if __name__ == "__main__":

# 	 # Resolve transcripts dir relative to THIS file: phase_1/transcripts
#     project_root = Path(__file__).resolve().parents[2]  # .../phase_1
#     transcripts_dir = project_root / "transcripts"

#     folder = Path(transcripts_dir)
#     docs = Chunks.parse_all_webvtt_in_dir(folder)
#     if docs:
#         print(f"Parsed {len(docs)} chunks. Sample chunk:")
#         print(docs[0])
#     else:
#         print("No cues parsed. Check file patterns or transcript format.")
