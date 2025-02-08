import logging
import pytest
from api.services.image_service import analyze_document_with_vision
from api.utils.image_utils import encode_image_to_base64, convert_pdf_to_images
import os

# Konfiguracja loggera
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

image_path = "/home/karol/Documents/dl-14a (2).pdf"  # Twoja ścieżka do PDF

def test_analyze_document():
    """
    Funkcja testująca analizę dokumentu z obrazem w Base64.
    """
    try:
        # Konwertowanie PDF do obrazów
        images = convert_pdf_to_images(image_path)

        # Wybieramy pierwszy obraz z listy (jeśli masz więcej niż jeden stronę w PDF)
        if not images:
            raise ValueError("Brak obrazów po konwersji PDF")

        image = images[0]  # Pierwsza strona PDF
        base64_image = encode_image_to_base64(image)

        # Wywołanie funkcji do analizy dokumentu
        result = analyze_document_with_vision(base64_image)

        # Assercja lub logowanie wyniku
        assert result is not None, "No result returned"
        logger.debug("Wynik analizy dokumentu:")
        logger.debug(result)

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
