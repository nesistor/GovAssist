import faiss
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List
from api.services.rag_utils import generate_answer_with_context

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

def load_embeddings_from_firestore():
    """
    Pobiera embeddingi i dokumenty z Firestore, a następnie buduje indeks FAISS.
    """
    embeddings = []
    doc_ids = []
    document_store = {}

    docs = db.collection("documents").stream()

    for doc in docs:
        data = doc.to_dict()
        embedding = np.array(data["embedding"], dtype=np.float32)
        doc_id = doc.id
        text = data["text"]

        embeddings.append(embedding)
        doc_ids.append(doc_id)
        document_store[doc_id] = text

    if not embeddings:
        raise ValueError("Brak embeddingów w Firestore!")

    # Tworzenie FAISS Index
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    return index, document_store


# **Ładowanie danych do FAISS**
faiss_index, document_store = load_embeddings_from_firestore()


def find_nearest_documents(query: str, top_k: int = 5) -> List[str]:
    """
    Wyszukuje najbliższe dokumenty w FAISS na podstawie embeddingu zapytania.
    """
    query_vector = np.array([query], dtype=np.float32)
    _, indices = faiss_index.search(query_vector, top_k)

    relevant_docs = [document_store.get(str(idx), "Brak danych") for idx in indices[0]]
    return relevant_docs


def retrieve_and_answer(query: str, ministry: str) -> Dict[str, str]:
    """
    Pobiera odpowiednie dokumenty dla danego ministerstwa i generuje odpowiedź.
    """
    relevant_docs = find_nearest_documents(query)

    if not relevant_docs:
        return {"answer": "Nie znaleziono odpowiednich dokumentów dla Twojego zapytania."}

    answer = generate_answer_with_context(query, relevant_docs)
    return {"answer": answer}

