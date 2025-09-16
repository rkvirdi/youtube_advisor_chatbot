import os
from src.utils.retriever import retrieve_relevant_chunks
from src.utils.generator import generate_response

def main():
    # Accept user query (CLI, API, etc.)
    user_query = input("Ask your question: ")

    # Retrieve relevant transcript chunks from Weaviate
    retrieved_chunks = retrieve_relevant_chunks(user_query)
    print(f"Retrieved {len(retrieved_chunks)} relevant chunks.")
    #print(retrieved_chunks)
    # Generate response using retrieved chunks (with citations)
    response = generate_response(user_query, retrieved_chunks)

    print("\nResponse:")
    print(response)

if __name__ == "__main__":
    main()