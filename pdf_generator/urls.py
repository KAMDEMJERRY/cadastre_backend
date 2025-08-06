from django.urls import path
from pdf_generator.views import GeneratePDFAPIView

urlpatterns = [
    path('generate-pdf/', GeneratePDFAPIView.as_view(), name='generate_pdf'),
 ]
 