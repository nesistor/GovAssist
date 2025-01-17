import os
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

# Initialize embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
model = SentenceTransformer(EMBEDDING_MODEL)

# Document Store
DOCUMENTS = {
    "dmv": [
        {"document_name": "Driver's License Application", "content": "Fill out the driver's license application form."},
        {"document_name": "Vehicle Registration Form", "content": "Complete the vehicle registration application."}
    ],
    "health": [
        {"document_name": "Healthcare Application Form", "content": "Apply for healthcare benefits using this form."},
        {"document_name": "Insurance Claim Form", "content": "Submit your insurance claim with this document."}
    ]
}

def index_documents(documents):
    """Index documents by creating embeddings."""
    indexed_data = {}
    for category, docs in documents.items():
        category_embeddings = []
        for doc in docs:
            chunks = [doc["content"]]  
            embeddings = model.encode(chunks)
            category_embeddings.append({"document_name": doc["document_name"], "chunks": chunks, "embeddings": embeddings})
        indexed_data[category] = category_embeddings
    return indexed_data

indexed_documents = index_documents(DOCUMENTS)

def retrieve_relevant_chunks(query, category):
    """Retrieve the most relevant chunks for a query."""
    try:
        if category not in indexed_documents:
            raise ValueError(f"Category '{category}' not found.")   

        query_embedding = model.encode([query])
        relevant_chunks = []
        
        for doc in indexed_documents[category]:
            similarities = cosine_similarity(query_embedding, doc["embeddings"])[0]
            best_match_idx = np.argmax(similarities)
            relevant_chunks.append({"document_name": doc["document_name"], "chunk": doc["chunks"][best_match_idx], "score": similarities[best_match_idx]})

        return sorted(relevant_chunks, key=lambda x: x["score"], reverse=True)

    except Exception as e:
        logger.error(f"Error in retrieving chunks: {str(e)}")
        return []
