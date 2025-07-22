from argparse import Action
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
<<<<<<< HEAD
from account.models import User
from lotissement.models import Bloc, Lotissement, Parcelle, Rue
from lotissement.serializers import BlocSerializer, LotissementSerializer, ParcelleSerializer, RueSerializer
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
=======
from account.models import IsAdministrateurCadastral, IsProprietaire, IsSuperAdministrateur, User
from lotissement.models import Bloc, Lotissement, Parcelle
from lotissement.serializers import BlocSerializer, LotissementSerializer, ParcelleSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
>>>>>>> 1b99f77 (Ajout des permissions aux vues)

# Create your views here.
class LotissementViewSet(viewsets.ModelViewSet):
    queryset = Lotissement.objects.all()
    serializer_class = LotissementSerializer
<<<<<<< HEAD
    permission_classes = [DjangoModelPermissions]
=======
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        return [IsAuthenticated()]
>>>>>>> 1b99f77 (Ajout des permissions aux vues)

    
class BlocViewSet(viewsets.ModelViewSet):
    queryset = Bloc.objects.all()
    serializer_class = BlocSerializer
<<<<<<< HEAD
    permission_classes = [DjangoModelPermissions]
=======
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        return [IsAuthenticated()]
>>>>>>> 1b99f77 (Ajout des permissions aux vues)


class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer
<<<<<<< HEAD
    permission_classes = [DjangoModelPermissions]
=======
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
>>>>>>> 1b99f77 (Ajout des permissions aux vues)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='administrateur').exists():
            return Parcelle.objects.all()
        return Parcelle.objects.filter(proprietaire=user)

class RueViewSet(viewsets.ModelViewSet):
    queryset = Rue.objects.all()
    serializer_class = RueSerializer
    permission_classes = [DjangoModelPermissions]
