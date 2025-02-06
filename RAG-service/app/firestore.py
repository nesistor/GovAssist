from settings import db
from embedding import get_embedding
import numpy as np

async def retrieve_relevant_docs(query: str):
    """Find top relevant docs using vector search"""
    query_embedding = await get_embedding(query)
    all_docs = db.collection("documents").stream()

    similarities = []
    for doc in all_docs:
        doc_data = doc.to_dict()
        embedding = doc_data.get("embedding", [0] * 1536)
        similarity = np.dot(query_embedding, embedding)
        similarities.append((similarity, doc_data))

    similarities.sort(reverse=True, key=lambda x: x[0])
    return [doc for _, doc in similarities[:5]]
