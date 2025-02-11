from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
from api.services.firebase_service import DocumentManager
import io
import logging

logger = logging.getLogger(__name__)

# Rejestracja czcionki odręcznej (pobierz np. "PatrickHand-Regular.ttf" i umieść w katalogu)
pdfmetrics.registerFont(TTFont("Handwriting", "PatrickHand-Regular.ttf"))

# Funkcja do wypełniania PDF odręcznym pismem
async def fill_pdf_dynamically(session_id: str, data: dict):
    try:
        # Pobierz metadane i plik PDF
        analysis = await DocumentManager.get_document_analysis(session_id)
        blob = bucket.blob(f"documents/{session_id}.pdf")
        pdf_data = blob.download_as_bytes()
        
        # Wczytaj PDF
        reader = PdfReader(io.BytesIO(pdf_data))
        writer = PdfWriter()
        
        # Przygotuj warstwę tekstu
        packet = io.BytesIO()
        c = canvas.Canvas(packet)
        c.setFont("Handwriting", 12)
        
        # Wypełnij pola na podstawie analizy
        for field in analysis['fields']:
            if field['field_name'] in data:
                x = field['position']['x']
                y = field['position']['y']
                c.drawString(x, y, str(data[field['field_name']]))
        
        c.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        
        # Połącz warstwy
        page = reader.pages[0]
        page.merge_page(new_pdf.pages[0])
        writer.add_page(page)
        
        # Zapisz wypełniony PDF
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        # Zapisz wynikowy plik
        result_blob = bucket.blob(f"filled_forms/{session_id}.pdf")
        result_blob.upload_from_string(output.read(), content_type='application/pdf')
        
        return result_blob.public_url
        
    except Exception as e:
        logger.error(f"Błąd wypełniania PDF: {str(e)}")
        raise

# Dane do wypełnienia
data = {
    "name": "John Doe",
    "address": "123 Main St, Springfield, IL"
}

fill_pdf_dynamically("session_id", data)
