from api.settings import db
from api.embeding import get_embedding
from api.faiss_index import search_faiss

async def retrieve_relevant_docs(query: str):
    """Znajdź najlepsze dokumenty używając FAISS"""
    query_embedding = await get_embedding(query)
    relevant_doc_ids = search_faiss(query_embedding, top_k=5)

    relevant_docs = []
    for doc_id in relevant_doc_ids:
        doc_ref = db.collection("documents").document(doc_id)
        doc_data = doc_ref.get().to_dict()
        if doc_data:
            relevant_docs.append(doc_data)

    return relevant_docs
