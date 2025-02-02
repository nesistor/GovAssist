from playwright.async_api import async_playwright
from openai import OpenAI
import os

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

async def scrape_with_ai(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        content = await page.inner_text("body")
        await browser.close()
    
    # Przetwarzanie treści przez AI
    response = client.chat.completions.create(
        model="grok-2-latest",
        messages=[{"role": "user", "content": f"Podsumuj tę treść: {content}"}],
        max_tokens=300
    )
    
    return response.choices[0].message

import asyncio
result = asyncio.run(scrape_with_ai("https://news.ycombinator.com"))
print(result)
