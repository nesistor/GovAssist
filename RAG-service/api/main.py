from fastapi import FastAPI
from api.firestore import retrieve_relevant_docs
from api.sitemap import get_ai_docs_urls

app = FastAPI()

@app.get("/docs/relevant")
async def get_relevant_docs(query: str):
    """Retrieve the most relevant documentation"""
    return await retrieve_relevant_docs(query)

@app.get("/docs/urls")
def get_documentation_urls():
    """Get all available documentation URLs"""
    return get_ai_docs_urls()
