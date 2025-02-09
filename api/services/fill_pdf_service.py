from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

async def fill_pdf_service(template_path: str, fields_data: dict) -> bytes:
    # Przenieś całą logikę wewnątrz tej funkcji
    reader = PdfReader(template_path)
    writer = PdfWriter()
    
    packet = BytesIO()
    c = canvas.Canvas(packet)
    
    for field in fields_data:
        x = field['position']['x']
        y = field['position']['y']
        value = field['value']
        
        if field['type'] == 'Checkbox' and value:
            c.drawString(x, y, "X")
        else:
            c.setFont("Helvetica", 12)
            c.drawString(x, y, str(value))
    
    c.save()
    
    new_pdf = PdfReader(packet)
    page = reader.pages[0]
    page.merge_page(new_pdf.pages[0])
    writer.add_page(page)
    
    output = BytesIO()
    writer.write(output)
    return output.getvalue() 