from argparse import Action
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from account.models import IsAdministrateurCadastral, IsProprietaire, IsSuperAdministrateur, User
from lotissement.models import Bloc, Lotissement, Parcelle, Rue
from lotissement.serializers import BlocSerializer, LotissementSerializer, ParcelleSerializer, RueSerializer
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions

# Create your views here.
class LotissementViewSet(viewsets.ModelViewSet):
    queryset = Lotissement.objects.all()
    serializer_class = LotissementSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        return [IsAuthenticated()]

    
class BlocViewSet(viewsets.ModelViewSet):
    queryset = Bloc.objects.all()
    serializer_class = BlocSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        return [IsAuthenticated()]


class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        
        elif self.action == 'create':
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        
        elif self.action == 'mes_parcelles':
            return [IsAuthenticated(), IsProprietaire()]
        
        elif self.action == 'parcelles_utilisateur':
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
    
        # Si l'utilisateur n'est pas authentifié, retourner un queryset vide
        if not user.is_authenticated:
            return Parcelle.objects.none()
        
        # Si l'utilisateur est superadmin OU a la permission IsSuperAdministrateur OU IsAdministrateurCadastrale
        if (user.is_superuser or 
            user.has_perm('account.IsSuperAdministrateur') or 
            user.has_perm('account.IsAdministrateurCadastrale')):
            return Parcelle.objects.all()
        
        # Sinon, retourner seulement les parcelles dont il est propriétaire
        return Parcelle.objects.filter(proprietaire=user)

class RueViewSet(viewsets.ModelViewSet):
    queryset = Rue.objects.all()
    serializer_class = RueSerializer
    permission_classes = [DjangoModelPermissions]
