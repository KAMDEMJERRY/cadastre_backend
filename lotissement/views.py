from argparse import Action
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from account.models import IsAdministrateurCadastral, IsAdministrateurCadastralOrSuperAdmin, IsProprietaire, IsSuperAdministrateur, User
from lotissement.models import Bloc, Lotissement, Parcelle, Rue
from lotissement.serializers import BlocSerializer, LotissementSerializer, ParcelleSerializer, RueSerializer
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
from rest_framework_gis.filters import InBBoxFilter
from rest_framework_gis.pagination import GeoJsonPagination
# Create your views here.
class LotissementViewSet(viewsets.ModelViewSet):
    queryset = Lotissement.objects.all()
    serializer_class = LotissementSerializer
    pagination_class = GeoJsonPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdministrateurCadastralOrSuperAdmin()]
        return [IsAuthenticated()]

    
class BlocViewSet(viewsets.ModelViewSet):
    queryset = Bloc.objects.all()
    serializer_class = BlocSerializer
    pagination_class = GeoJsonPagination
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdministrateurCadastralOrSuperAdmin()]
        return [IsAuthenticated()]


class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer
    pagination_class = GeoJsonPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        
        elif self.action == 'create':
            return [IsAuthenticated(), IsAdministrateurCadastralOrSuperAdmin()]
        
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdministrateurCadastralOrSuperAdmin()]
        
        elif self.action == 'mes_parcelles':
            return [IsAuthenticated(), IsProprietaire()]
        
        elif self.action == 'parcelles_utilisateur':
            return [IsAuthenticated(), IsAdministrateurCadastralOrSuperAdmin()]
        
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
    
        # Si l'utilisateur n'est pas authentifié, retourner un queryset vide
        if not user.is_authenticated:
            return Parcelle.objects.none()
        
        # Si l'utilisateur est superadmin OU a la permission IsSuperAdministrateur OU IsAdministrateurCadastrale
        if (user.is_superuser or 
            user.groups.filter(name='AdministrateurCadastral').exists()):
            return Parcelle.objects.all()
        
        # Sinon, retourner seulement les parcelles dont il est propriétaire
        return Parcelle.objects.filter(proprietaire=user)

class RueViewSet(viewsets.ModelViewSet):
    pagination_class = GeoJsonPagination

    queryset = Rue.objects.all()
    serializer_class = RueSerializer
    permission_classes = [DjangoModelPermissions]
