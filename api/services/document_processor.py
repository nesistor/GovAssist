from typing import List

def split_document_into_chunks(document: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Splits a document into smaller chunks for embedding.

    Args:
        document (str): The document text.
        chunk_size (int): The desired size of each chunk (in characters).
        overlap (int): The number of overlapping characters between chunks.

    Returns:
        List[str]: A list of document chunks.
    """
    chunks = []
    for i in range(0, len(document), chunk_size - overlap):
        chunk = document[i:i + chunk_size]
        chunks.append(chunk)
    return chunks