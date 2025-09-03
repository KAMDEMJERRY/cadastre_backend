from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from parcelledoc.models import Document
from parcelledoc.serializers import DocumentSerializer

# Create your views here.

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(detail=False, methods=['GET'], url_path="parcelleDoc", )
    @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'parcelle_id',
            openapi.IN_QUERY,
            description="ID de la parcelle pour récupérer le document",
            type=openapi.TYPE_NUMBER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Document trouvé', DocumentSerializer),
        400: openapi.Response('Paramètre manquant'),
        404: openapi.Response('Document non trouvé')
    }
)
    def getDocByParcelleId(self, request):
        parcelle_id =  request.query_params.get("parcelle_id")
        if not parcelle_id:
           return Response({"Error": "Parcelle_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
             document = self.queryset.get(parcelle = int(parcelle_id))
             serializer = self.get_serializer(document);
             return Response(serializer.data)
        except self.queryset.model.DoesNotExist:
            return Response({"Error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Erreur": "Erreur serveur" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                