import os
import logging
import chromadb
from openai import OpenAI
from typing import List
from api.services.document_processor import split_document_into_chunks

# Configure logging
logger = logging.getLogger(__name__)

# xAI API Key
XAI_API_KEY = os.getenv("XAI_API_KEY")
EMBEDDING_MODEL_NAME = "v1"  # Embedding model

# Initialize OpenAI client for embedding
embedding_client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

# Initialize ChromaDB client
chroma_client = chromadb.Client()
collection_name = "ministry_documents"
collection = None  # Initialize collection to None


def get_or_create_collection():
    """Gets the ChromaDB collection, creating it if it doesn't exist."""
    global collection
    if collection is None:
        try:
            collection = chroma_client.get_collection(name=collection_name)
            logger.info(f"Collection '{collection_name}' retrieved.")
        except ValueError:
            collection = chroma_client.create_collection(name=collection_name)
            logger.info(f"Collection '{collection_name}' created.")
    return collection

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generates embeddings for a list of texts using the xAI API."""
    try:
        response = embedding_client.embeddings.create(
            input=texts,
            model=EMBEDDING_MODEL_NAME,
            encoding_format="float"
        )
        embeddings = [item.embedding for item in response.data]
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise


def add_documents_to_collection(documents: dict):
    """Adds documents to the ChromaDB collection.

    Args:
        documents (dict): A dictionary where keys are ministry names and values are
                          lists of document strings.
    """
    collection = get_or_create_collection()
    for ministry, docs in documents.items():
        for doc in docs:
            chunks = split_document_into_chunks(doc)
            ids = [f"{ministry}_{doc_id}" for doc_id in range(len(chunks))]
            embeddings = generate_embeddings(chunks)

            # Prepare metadata for each chunk
            metadatas = [{"ministry": ministry, "document_part": str(i)} for i in range(len(chunks))]

            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(chunks)} chunks for ministry '{ministry}' to collection")


def query_collection(query_text: str, n_results: int = 5, ministry_filter: str = None) -> dict:
    """Queries the ChromaDB collection for similar text chunks."""
    collection = get_or_create_collection()
    query_embedding = generate_embeddings([query_text])[0]

    # Build where clause for metadata filtering
    where_clause = {}
    if ministry_filter:
        where_clause["ministry"] = ministry_filter

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_clause
    )
    return results