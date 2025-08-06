from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from pdf_service import PDFService
from serializers import PDFGenerateSerializer
from rest_framework.permissions import IsAuthenticated


class GeneratePDFAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PDFGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try: 
            pdf_type = serializer.validated_data['type']
            data = serializer.validated_data['data']
            if pdf_type == 'simple':
                pdf_type = PDFService.generate_simple_pdf(data['content'])
            elif pdf_type == 'template':
                pdf_type = PDFService.generate_advanced_pdf(data['template_name'], data['context'])
            elif pdf_type == 'table':
                pdf_type = PDFService.generate_table_pdf(data['data'], data.get('title', "Rapport des Parcelles"))
            else:
                return Response({'error': 'Invalid PDF type'}, status=status.HTTP_400_BAD_REQUEST)

            response = HttpResponse(pdf_type, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
            return response
        
        except Exception as e:
            return Response ({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Create your views here.
