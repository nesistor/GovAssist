import openai
from settings import XAI_API_KEY, XAI_API_BASE, XAI_MODEL

# Configure OpenAI SDK
openai.api_key = XAI_API_KEY
openai.api_base = XAI_API_BASE

async def get_embedding(text: str):
    """Get embedding vector from OpenAI via x.ai"""
    try:
        response = await openai.Embedding.acreate(
            model=XAI_MODEL,
            input=text,
            encoding_format="float"
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error
