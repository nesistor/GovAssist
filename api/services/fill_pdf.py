from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO

# Function to fill PDF
def fill_pdf(input_pdf_path, output_pdf_path, data):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Create a PDF canvas for the new document
    packet = BytesIO()
    c = canvas.Canvas(packet)
    
    # Example: Filling in the "Name" field
    c.drawString(100, 750, data['name'])  # Position (100, 750) is an example
    c.drawString(100, 730, data['address'])
    # Add other fields here...

    c.save()
    
    packet.seek(0)
    new_pdf = PdfReader(packet)
    page = reader.pages[0]

    # Merge the original page with the filled data
    page.merge_page(new_pdf.pages[0])

    writer.add_page(page)

    # Save the new filled PDF
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

# Example data to fill the form
data = {
    "name": "John Doe",
    "address": "123 Main St, Springfield, IL"
}

fill_pdf("input_form.pdf", "filled_form.pdf", data)
