def generate_response(user_query, retrieved_chunks):
	"""
	Generate a response using retrieved transcript chunks, including citations.
	retrieved_chunks: list of dicts with keys 'text', 'video_id', 'start', 'end', 'source'
	"""
	if not retrieved_chunks:
		return "No relevant information found in the transcripts. Please clarify your question."

	response_parts = []
	citations = []
	for chunk in retrieved_chunks:
		# Add chunk text to response
		response_parts.append(chunk['text'])
		# Format citation
		citations.append(f"[source: {chunk['video_id']} t={chunk['start']}–{chunk['end']}]")

	response_text = "\n---\n".join(response_parts)
	citation_text = "\n".join(citations)

	return f"Answer based on retrieved transcript chunks:\n\n{response_text}\n\nCitations:\n{citation_text}"
