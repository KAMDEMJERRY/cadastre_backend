from argparse import Action
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from account.models import IsAdministrateurCadastralOrSuperAdmin, IsProprietaire, IsSuperAdministrateur, User
from lotissement.models import Bloc, Lotissement, Parcelle, Rue
from lotissement.serializers import BlocSerializer, BlocStatsSerializer, LotissementDetailSerializer, LotissementSerializer, LotissementStatsSerializer, ParcelleSerializer, RueSerializer
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
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
            user.groups.filter(name='administrateurs_cadastraux').exists()):
            parcelles =  Parcelle.objects.all()
            return parcelles
        
        # Sinon, retourner seulement les parcelles dont il est propriétaire
        return Parcelle.objects.filter(proprietaire=user)

class RueViewSet(viewsets.ModelViewSet):
    pagination_class = GeoJsonPagination

    queryset = Rue.objects.all()
    serializer_class = RueSerializer
    permission_classes = [DjangoModelPermissions]


class LotissementStatsListView(generics.ListAPIView):
    """
    API qui retourne pour chaque lotissement le nombre de blocs et de parcelles
    """
    serializer_class = LotissementStatsSerializer
    
    def get_queryset(self):
        return Lotissement.objects.annotate(
            nombre_blocs=Count('bloc', distinct=True),
            nombre_parcelles=Count('bloc__parcelles', distinct=True)
        )

class BlocStatsListView(generics.ListAPIView):
    """
    API qui retourne pour chaque bloc le nombre de parcelles
    """
    serializer_class = BlocStatsSerializer
    
    def get_queryset(self):
        return Bloc.objects.annotate(
            nombre_parcelles=Count('parcelles', distinct=True)
        )

class LotissementDetailView(generics.RetrieveAPIView):
    """
    Détail d'un lotissement avec statistiques complètes
    """
    queryset = Lotissement.objects.all()
    serializer_class = LotissementDetailSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return Lotissement.objects.annotate(
            blocs_count=Count('bloc', distinct=True),
            parcelles_count=Count('bloc__parcelles', distinct=True)
        )

@api_view(['GET'])
def lotissement_stats_detail(request, lotissement_id):
    """
    API détaillée pour un lotissement spécifique
    """
    try:
        lotissement = Lotissement.objects.filter(id=lotissement_id).annotate(
            nombre_blocs=Count('bloc', distinct=True),
            nombre_parcelles=Count('bloc__parcelles', distinct=True)
        ).first()
        
        if not lotissement:
            return Response(
                {'error': 'Lotissement non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = LotissementStatsSerializer(lotissement)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def bloc_stats_detail(request, bloc_id):
    """
    API détaillée pour un bloc spécifique
    """
    try:
        bloc = Bloc.objects.filter(id=bloc_id).annotate(
            nombre_parcelles=Count('parcelles', distinct=True)
        ).first()
        
        if not bloc:
            return Response(
                {'error': 'Bloc non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BlocStatsSerializer(bloc)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def global_stats(request):
    """
    Statistiques globales de tous les lotissements et blocs
    """
    # Statistiques par lotissement
    lotissements = Lotissement.objects.annotate(
        blocs_count=Count('bloc', distinct=True),
        parcelles_count=Count('bloc__parcelles', distinct=True)
    ).values('id', 'name', 'blocs_count', 'parcelles_count')
    
    # Statistiques par bloc
    blocs = Bloc.objects.annotate(
        parcelles_count=Count('parcelles', distinct=True)
    ).values('id', 'name', 'bloc_lotissement__name', 'parcelles_count')
    
    return Response({
        'lotissements': list(lotissements),
        'blocs': list(blocs),
        'total_lotissements': Lotissement.objects.count(),
        'total_blocs': Bloc.objects.count(),
        'total_parcelles': Parcelle.objects.count()
    })
    