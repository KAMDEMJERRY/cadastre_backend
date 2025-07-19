from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type_proprietaire', 'role', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(prenom__icontains=search) |
                Q(email__icontains=search) |
                Q(cni__icontains=search)
            )
        return queryset
    
    @action(detail=False, methods=['get'])
    def proprietaires(self, request):
        """Récupérer uniquement les propriétaires"""
        proprietaires = self.queryset.filter(role='proprietaire')
        serializer = self.get_serializer(proprietaires, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def admins(self, request):
        """Récupérer uniquement les admins"""
        admins = self.queryset.filter(role='admin')
        serializer = self.get_serializer(admins, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activer un utilisateur"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'Utilisateur activé'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Désactiver un utilisateur"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'Utilisateur désactivé'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des utilisateurs"""
        total = self.queryset.count()
        active = self.queryset.filter(is_active=True).count()
        proprietaires = self.queryset.filter(role='proprietaire').count()
        admins = self.queryset.filter(role='admin').count()
        public = self.queryset.filter(type_proprietaire='public').count()
        prive = self.queryset.filter(type_proprietaire='prive').count()
        
        return Response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'proprietaires': proprietaires,
            'admins': admins,
            'public': public,
            'prive': prive
        })