import openai
from settings import OPENAI_EMBEDDING_API_KEY, OPENAI_API_BASE, OPENAI_MODEL

# Configure OpenAI SDK
openai.api_key = OPENAI_EMBEDDING_API_KEY
openai.api_base = OPENAI_API_BASE

async def get_embedding(text: str):
    """Get embedding vector from OpenAI via x.ai"""
    try:
        response = await openai.Embedding.acreate(
            model=OPENAI_MODEL,
            input=text,
            encoding_format="float"
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error
