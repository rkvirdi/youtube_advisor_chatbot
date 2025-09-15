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