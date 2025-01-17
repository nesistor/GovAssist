from api.services.embedding_service import query_collection
from typing import List
from openai import OpenAI
import os

# xAI API Key (make sure this is set in your environment variables)
XAI_API_KEY = os.getenv("XAI_API_KEY")
CHAT_MODEL_NAME = "grok-2-latest"

# Initialize OpenAI client for answer generation within the tool
rag_client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")


def retrieve_relevant_documents(query: str, ministry: str, n_results: int = 3) -> List[str]:
    """Retrieves relevant document chunks from the vector database based on the query and ministry."""
    results = query_collection(query, n_results=n_results, ministry_filter=ministry)
    retrieved_docs = results['documents'][0]
    return retrieved_docs


def generate_answer_with_context(query: str, context_documents: List[str]) -> str:
    """Generates an answer to the query using the provided context documents."""
    context_str = " ".join(context_documents)
    augmented_prompt = f"Based on the following context: '{context_str}', answer the question: '{query}'"

    try:
        response = rag_client.chat.completions.create(  
            model=CHAT_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided context documents."
                },
                {
                    "role": "user",
                    "content": augmented_prompt
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating answer with context: {e}")
        return "I couldn't find an answer based on the provided documents."