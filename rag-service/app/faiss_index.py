# faiss_index.py
import faiss
import numpy as np
import os
from typing import List, Union

class FaissIndexManager:
    def __init__(self, index_path: str = "faiss_index.index", dimension: int = 1536):
        self.index_path = index_path
        self.dimension = dimension
        self.index = self._initialize_index()

    def _initialize_index(self) -> faiss.IndexIDMap:
        """Inicjalizuje lub wczytuje istniejący indeks FAISS"""
        if os.path.exists(self.index_path):
            print(f"Wczytuję istniejący indeks FAISS z {self.index_path}")
            return faiss.read_index(self.index_path)
        else:
            print(f"Tworzę nowy indeks FAISS ({self.dimension} wymiarów)")
            base_index = faiss.IndexFlatIP(self.dimension)  # Inner Product dla podobieństwa cosinusowego
            return faiss.IndexIDMap(base_index)

    def add_embeddings(self, embeddings: List[List[float]], ids: List[int]):
        """
        Dodaje embeddingi do indeksu FAISS
        :param embeddings: Lista wektorów embeddingów
        :param ids: Lista odpowiadających im ID (muszą być unikalne)
        """
        if len(embeddings) != len(ids):
            raise ValueError("Liczba embeddingów i ID musi być taka sama")

        # Konwersja do numpy array i normalizacja
        embeddings_np = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_np)  # Normalizacja dla Inner Product (cosine similarity)

        # Konwersja ID do formatu akceptowanego przez FAISS
        ids_np = np.array(ids, dtype=np.int64)

        # Dodawanie do indeksu
        self.index.add_with_ids(embeddings_np, ids_np)
        self._save_index()

    def search(self, query_embedding: List[float], k: int = 5) -> List[tuple]:
        """
        Wyszukuje najbliższych sąsiadów w indeksie
        :param query_embedding: Wektor zapytania
        :param k: Liczba wyników do zwrócenia
        :return: Lista krotek (score, id)
        """
        # Normalizacja wektora zapytania
        query_np = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_np)

        # Wyszukiwanie
        distances, indices = self.index.search(query_np, k)
        
        # Formatowanie wyników
        return list(zip(distances[0], indices[0]))

    def _save_index(self):
        """Zapisuje indeks na dysk"""
        faiss.write_index(self.index, self.index_path)
        print(f"Zapisano indeks FAISS do {self.index_path}")

    def get_index_stats(self) -> dict:
        """Zwraca statystyki indeksu"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.index.d,
            "is_trained": self.index.is_trained
        }

# Przykład użycia:
if __name__ == "__main__":
    # Testowa konfiguracja
    index_manager = FaissIndexManager()
    
    # Przykładowe dane testowe
    test_embeddings = [
        [0.1] * 1536,
        [0.2] * 1536
    ]
    test_ids = [1, 2]
    
    # Dodawanie danych testowych
    index_manager.add_embeddings(test_embeddings, test_ids)
    
    # Wyszukiwanie testowe
    results = index_manager.search([0.15]*1536)
    print("Wyniki wyszukiwania:", results)
    
    # Statystyki
    print("Statystyki indeksu:", index_manager.get_index_stats())