import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlparse
from datetime import datetime, timezone

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from google.cloud import firestore
from openai import AsyncOpenAI
from aimlapi import OpenAI  # Importing the new OpenAI class

from settings import (
    OPENAI_API_KEY,
    LLM_MODEL,
    FIREBASE_CREDENTIALS_PATH,
)
from utils import chunk_text, get_embedding, get_title_and_summary

# Initialize OpenAI client using aimlapi
api_key = "my_key"
base_url = "https://api.aimlapi.com/v1"
api = OpenAI(api_key=api_key, base_url=base_url)

# Initialize Firestore client
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

@dataclass
class ProcessedChunk:
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: Dict[str, Any]

async def process_chunk(
    chunk: str, chunk_number: int, url: str, source: str
) -> ProcessedChunk:
    """Process a single chunk of text."""
    # Get title and summary
    extracted = await get_title_and_summary(chunk, url, api, LLM_MODEL)  # Updated to use the new API client

    # Create metadata
    metadata = {
        "source": source,
        "chunk_size": len(chunk),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "url_path": urlparse(url).path,
    }

    return ProcessedChunk(
        url=url,
        chunk_number=chunk_number,
        title=extracted["title"],
        summary=extracted["summary"],
        content=chunk,  # Store the original chunk content
        metadata=metadata,
    )

async def insert_chunk(chunk: ProcessedChunk):
    """Insert a processed chunk into Firestore."""
    try:
        doc_ref = db.collection("site_pages").document()
        await doc_ref.set(
            {
                "url": chunk.url,
                "chunk_number": chunk.chunk_number,
                "title": chunk.title,
                "summary": chunk.summary,
                "content": chunk.content,
                "metadata": chunk.metadata,
            }
        )
        print(f"Inserted chunk {chunk.chunk_number} for {chunk.url}")
    except Exception as e:
        print(f"Error inserting chunk: {e}")

async def process_and_store_document(url: str, markdown: str, source: str):
    """Process a document and store its chunks in parallel."""
    # Split into chunks
    chunks = chunk_text(markdown)

    # Process chunks in parallel
    tasks = [process_chunk(chunk, i, url, source) for i, chunk in enumerate(chunks)]
    processed_chunks = await asyncio.gather(*tasks)

    # Store chunks in parallel
    insert_tasks = [insert_chunk(chunk) for chunk in processed_chunks]
    await asyncio.gather(*insert_tasks)

async def crawl_website(
    url: str,
    crawler: AsyncWebCrawler,
    crawl_config: CrawlerRunConfig,
    source: str,
):
    """Crawls a single website and stores the data."""
    try:
        result = await crawler.arun(
            url=url,
            config=crawl_config,
            session_id="session1",
        )
        if result.success:
            print(f"Successfully crawled: {url}")
            await process_and_store_document(
                url, result.markdown_v2.raw_markdown, source
            )
        else:
            print(f"Failed: {url} - Error: {result.error_message}")
    except Exception as e:
        print(f"Error crawling {url}: {e}")

async def crawl_parallel(urls: List[str], max_concurrent: int = 5):
    """Crawl multiple URLs in parallel with a concurrency limit."""
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_url(url: str):
            async with semaphore:
                # Determine source from URL
                source = urlparse(url).netloc
                await crawl_website(url, crawler, crawl_config, source)

        # Process all URLs in parallel with limited concurrency
        await asyncio.gather(*[process_url(url) for url in urls])
    finally:
        await crawler.close()

def get_website_urls() -> List[str]:
    """Pobiera listę adresów URL stron do crawlowania."""
    # Zaimplementuj logikę pobierania listy, np. z pliku:
    with open("website_list.txt", "r") as f:
        urls = [line.strip() for line in f]
    return urls

async def main():
    # Get URLs from Firestore or a file
    urls = get_website_urls()
    if not urls:
        print("No URLs found to crawl")
        return

    print(f"Found {len(urls)} URLs to crawl")
    await crawl_parallel(urls)

if __name__ == "__main__":
    asyncio.run(main())
