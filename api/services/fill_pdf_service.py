from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

def fill_pdf_with_dynamic_fields(template_path, fields_data):
    reader = PdfReader(template_path)
    writer = PdfWriter()
    
    packet = BytesIO()
    c = canvas.Canvas(packet)
    
    for field in fields_data:
        x = field['position']['x']
        y = field['position']['y']
        value = field['value']
        
        # Dostosuj renderowanie do typu pola
        if field['type'] == 'Checkbox':
            if value:
                c.drawString(x, y, "X")
        else:
            c.setFont("Helvetica", 12)
            c.drawString(x, y, str(value))
    
    c.save()
    
    # ... reszta logiki scalania PDF ... 