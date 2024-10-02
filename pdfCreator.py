from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf_with_form(output_pdf_path):
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Add some basic text
    c.drawString(100, 750, "Please fill out the form below:")

    # Add 'Name' field
    c.drawString(100, 720, "Name:")
    c.acroForm.textfield(name='name_field', tooltip='Name', x=100, y=700, width=300, height=20)

    # Add 'Email' field
    c.drawString(100, 670, "Email:")
    c.acroForm.textfield(name='email_field', tooltip='Email', x=100, y=650, width=300, height=20)

    # Add 'Date' field
    c.drawString(100, 620, "Date:")
    c.acroForm.textfield(name='date_field', tooltip='Date', x=100, y=600, width=300, height=20)

    # Save the PDF
    c.save()

# Output path
output_pdf_path = "form_with_fields.pdf"
create_pdf_with_form(output_pdf_path)