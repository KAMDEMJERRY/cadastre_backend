from argparse import Action
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from account.models import User
from lotissement.models import Bloc, Lotissement, Parcelle, Rue
from lotissement.serializers import BlocSerializer, LotissementSerializer, ParcelleSerializer, RueSerializer
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions

# Create your views here.
class LotissementViewSet(viewsets.ModelViewSet):
    queryset = Lotissement.objects.all()
    serializer_class = LotissementSerializer
    permission_classes = [DjangoModelPermissions]

    
class BlocViewSet(viewsets.ModelViewSet):
    queryset = Bloc.objects.all()
    serializer_class = BlocSerializer
    permission_classes = [DjangoModelPermissions]


class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer
    permission_classes = [DjangoModelPermissions]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='administrateur').exists():
            return Parcelle.objects.all()
        return Parcelle.objects.filter(proprietaire=user)

class RueViewSet(viewsets.ModelViewSet):
    queryset = Rue.objects.all()
    serializer_class = RueSerializer
    permission_classes = [DjangoModelPermissions]
