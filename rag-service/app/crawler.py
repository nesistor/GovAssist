import os
import sys
import json
import asyncio
import requests
from xml.etree import ElementTree
from datetime import datetime, timezone
from urllib.parse import urlparse
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from openai import AsyncOpenAI
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Inicjalizacja klientów Firebase
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Konfiguracja dwóch różnych klientów OpenAI
xai_client = AsyncOpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

aiml_client = AsyncOpenAI(
    api_key=os.getenv("AIML_API_KEY"),
    base_url="https://api.aimlapi.com/v1"
)

def chunk_text(text: str, chunk_size: int = 5000) -> list[str]:
    """Inteligentny podział tekstu na fragmenty z uwzględnieniem struktury"""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Szukaj naturalnych granic
        last_break = max(
            text.rfind('\n\n', start, end),
            text.rfind('. ', start, end),
            text.rfind('```', start, end)
        )
        
        if last_break > start + chunk_size * 0.3:
            end = last_break + 1
            
        chunks.append(text[start:end].strip())
        start = end
        
    return chunks

async def generate_title_summary(chunk: str, url: str) -> dict:
    """Generuje tytuł i podsumowanie używając modelu AIML"""
    try:
        response = await aiml_client.chat.completions.create(
            model=os.getenv("AIML_MODEL", "gpt-4o-mini"),
            messages=[{
                "role": "system",
                "content": "Wygeneruj zwięzły tytuł i podsumowanie dla fragmentu dokumentacji."
            }, {
                "role": "user",
                "content": f"URL: {url}\nTreść:\n{chunk[:2000]}..."
            }],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Błąd generowania metadanych: {e}")
        return {"title": "Błąd", "summary": "Błąd przetwarzania"}

async def generate_embedding(text: str) -> list[float]:
    """Tworzy embedding przy użyciu modelu XAI"""
    try:
        response = await xai_client.embeddings.create(
            model="v1",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Błąd generowania embeddingu: {e}")
        return [0.0] * 1536

async def process_chunk(chunk: str, idx: int, url: str):
    """Przetwarza i zapisuje pojedynczy fragment dokumentacji"""
    metadata = await generate_title_summary(chunk, url)
    embedding = await generate_embedding(chunk)
    
    doc_data = {
        "url": url,
        "chunk_number": idx,
        "title": metadata.get("title", ""),
        "summary": metadata.get("summary", ""),
        "content": chunk,
        "embedding": embedding,
        "metadata": {
            "source": "pydantic_ai_docs",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "url_path": urlparse(url).path,
            "chunk_size": len(chunk)
        }
    }
    
    # Generowanie unikalnego ID dokumentu
    doc_id = f"{urlparse(url).path[1:].replace('/', '_')}_{idx}"
    
    try:
        db.collection("document_chunks").document(doc_id).set(doc_data)
        print(f"Zapisano fragment {idx} z {url}")
    except Exception as e:
        print(f"Błąd zapisu do Firestore: {e}")

async def process_document(url: str, content: str):
    """Przetwarza cały dokument"""
    chunks = chunk_text(content)
    tasks = [process_chunk(chunk, i, url) for i, chunk in enumerate(chunks)]
    await asyncio.gather(*tasks)

async def crawl_urls(urls: list[str], max_concurrent: int = 5):
    """Przetwarzanie wielu URLi równolegle"""
    crawler = AsyncWebCrawler(
        browser_config=BrowserConfig(
            headless=True,
            verbose=False,
            # Usunięto nieistniejący parametr logger
            extra_args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        ),
        run_config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            screenshot=False,
        )
    )
    
    await crawler.start()
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def crawl_task(url: str):
        async with semaphore:
            try:
                result = await crawler.arun(
                    url=url,
                    session_id="main",
                    bypass_cache=True,
                    timeout=30  # Dodano timeout
                )
                if result and result.success:
                    await process_document(url, result.markdown_v2.raw_markdown)
                else:
                    print(f"Błąd crawlowania: {url} - {getattr(result, 'error_message', 'Unknown error')}")
            except Exception as e:
                print(f"Krytyczny błąd dla {url}: {str(e)}")

    await asyncio.gather(*[crawl_task(url) for url in urls])
    await crawler.close()

def get_sitemap_urls(sitemap_url: str) -> list[str]:
    """Pobiera listę URLi z sitemap.xml"""
    try:
        response = requests.get(sitemap_url)
        root = ElementTree.fromstring(response.content)
        return [elem.text for elem in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    except Exception as e:
        print(f"Błąd pobierania sitemapy: {e}")
        return []

async def main():
    urls = get_sitemap_urls("https://azdot.gov/sitemap.xml")
    if not urls:
        print("Brak URLi do przetworzenia")
        return
    
    print(f"Rozpoczynam przetwarzanie {len(urls)} stron")
    await crawl_urls(urls)

if __name__ == "__main__":
    asyncio.run(main())