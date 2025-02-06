import json
import asyncio
from datetime import datetime, timezone
from urllib.parse import urlparse

from settings import db
from embedding import get_embedding
import openai

openai.api_key = AIML_API_KEY
openai.api_base = AIML_API_BASE

async def chunk_text(text: str, chunk_size: int = 5000):
    """Splits text into smart chunks, considering code blocks and paragraphs."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        chunk = text[start:end]
        last_break = max(chunk.rfind('\n\n'), chunk.rfind('. '))
        end = start + (last_break if last_break > chunk_size * 0.3 else chunk_size)
        chunks.append(text[start:end].strip())
        start = end
    return chunks

async def get_title_and_summary(chunk: str, url: str):
    """Extract title and summary using GPT-4."""
    system_prompt = """Extract a concise title and summary from the given chunk of documentation."""
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"URL: {url}\n\n{chunk[:1000]}..."}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error processing title & summary: {e}")
        return {"title": "Unknown", "summary": "Error extracting summary"}

async def process_chunk(chunk: str, chunk_number: int, url: str):
    """Process text chunk: extract title, summary, embedding & store in Firestore."""
    extracted = await get_title_and_summary(chunk, url)
    embedding = await get_embedding(chunk)
    metadata = {
        "source": "pydantic_ai_docs",
        "chunk_size": len(chunk),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url_path": urlparse(url).path
    }
    doc_ref = db.collection("documents").document(f"{url}_chunk{chunk_number}")
    doc_ref.set({
        "url": url,
        "chunk_number": chunk_number,
        "title": extracted["title"],
        "summary": extracted["summary"],
        "content": chunk,
        "metadata": metadata,
        "embedding": embedding
    })
    print(f"Stored chunk {chunk_number} for {url}")
