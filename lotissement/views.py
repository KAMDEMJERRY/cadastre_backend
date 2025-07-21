from argparse import Action
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from account.models import User
from lotissement.models import Bloc, Lotissement, Parcelle
from lotissement.serializers import BlocSerializer, LotissementSerializer, ParcelleSerializer
from rest_framework.decorators import action

# Create your views here.
class LotissementViewSet(viewsets.ModelViewSet):
    queryset = Lotissement.objects.all()
    serializer_class = LotissementSerializer

class BlocViewSet(viewsets.ModelViewSet):
    queryset = Bloc.objects.all()
    serializer_class = BlocSerializer

class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer

    @action(detail=False, methods=['get'])
    def mes_parcelles(self, request):
        """Récupère toutes les parcelles de l'utilisateur connecté"""
        parcelles = self.queryset.filter(proprietaire=request.user)
        serializer = self.get_serializer(parcelles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def parcelles_utilisateur(self, request, user_id=None):
        """Récupère les parcelles d'un utilisateur spécifique (admin seulement)"""
        user = get_object_or_404(User, id=user_id)
        parcelles = self.queryset.filter(proprietaire=user)
        serializer = self.get_serializer(parcelles, many=True)
        return Response(serializer.data)