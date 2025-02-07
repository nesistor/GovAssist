import faiss
import numpy as np

# FAISS Index dla embeddingów o wymiarze 1536
d = 1536
index = faiss.IndexFlatL2(d)  # L2 - dystans euklidesowy

# Mapa ID dokumentów -> indeksy FAISS
doc_id_mapping = {}

def add_embeddings_to_faiss(embeddings, doc_ids):
    """Dodaje embeddingi do FAISS i mapuje ich ID"""
    global index, doc_id_mapping
    embeddings = np.array(embeddings, dtype=np.float32)
    index.add(embeddings)
    
    # Mapowanie ID dokumentów na indeksy FAISS
    start_index = len(doc_id_mapping)
    for i, doc_id in enumerate(doc_ids):
        doc_id_mapping[start_index + i] = doc_id

def search_faiss(query_embedding, top_k=5):
    """Wyszukuje top K najbardziej podobnych dokumentów"""
    query_embedding = np.array([query_embedding], dtype=np.float32)
    if index.ntotal == 0:
        return []  # Brak danych w FAISS

    distances, indices = index.search(query_embedding, top_k)
    
    # Konwersja indeksów FAISS na `document_id`
    relevant_doc_ids = [doc_id_mapping.get(idx, None) for idx in indices[0] if idx != -1]
    return [doc_id for doc_id in relevant_doc_ids if doc_id]
