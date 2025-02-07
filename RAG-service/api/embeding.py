import openai
from api.settings import XAI_API_KEY, XAI_API_BASE, XAI_MODEL

# Konfiguracja OpenAI SDK
openai.api_key = XAI_API_KEY
openai.api_base = XAI_API_BASE

async def get_embedding(text: str):
    """Uzyskaj wektor embeddingu z OpenAI via x.ai"""
    try:
        response = await openai.Embedding.acreate(
            model=XAI_MODEL,
            input=text
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Błąd przy pobieraniu embeddingu: {e}")
        return [0.0] * 1536  # Zwróć wektor zerowy w przypadku błędu
