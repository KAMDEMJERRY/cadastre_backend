from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle, SimpleDocTemplate, Table
from django.template.loader import render_to_string
from xhtml2pdf import pisa

class PDFService:
    @staticmethod
    def generate_simple_pdf(content):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        # Configuration du PDF
        p.setFont("Helvetica", 12)
        p.drawString(100, 800, 'Document Genere')
        p.drawString(100, 780, content)

        p.showPage()
        p.save()    
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_advanced_pdf(template_name, context):
        buffer = BytesIO()
        html_content = render_to_string(template_name, context)
        buffer = BytesIO()
        pdf = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=buffer)

        if not pdf.err:
            buffer.seek(0)
            return buffer
        else:
            raise Exception("Error generating PDF: " + str(pdf.err))

    @staticmethod
    def generate_table_pdf(data, title="Rapport des Parcelles"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        elements.append(Paragraph(title, styles['Title']))

        keys = list(data[0].keys())
        table_data = [keys]
        for i, item in enumerate(data):
            table_data.append( [ item[key] for key in keys] )

        table = Table(table_data)
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return buffer
