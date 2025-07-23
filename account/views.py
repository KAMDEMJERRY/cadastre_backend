from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import IsAdministrateurCadastral, IsProprietaire, IsSuperAdministrateur
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs avec :
    - Gestion des types de compte (Individu/Organisation)
    - Filtres avancés
    - Actions personnalisées
    """

    def get_queryset(self):
        return User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'account_type', 
        'genre',
        'is_active',
        'domaine'
    ]
    
    # Permissions par action
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        
        elif self.action == 'create':
            # Seuls les admins cadastraux ou superadmins peuvent créer
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Admin cadastraux et superadmins uniquement
            return [IsAuthenticated(), IsAdministrateurCadastral() | IsSuperAdministrateur()]
        
        elif self.action == 'export_pdf':
            # Seuls les propriétaires peuvent exporter leur propre parcelle
            return [IsAuthenticated(), IsProprietaire()]
        
        return [IsAuthenticated()]

    # Sérialiseurs spécifiques
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    # Filtrage avancé
    def get_queryset(self):
        queryset = User.object.all()
        search = self.request.query_params.get('search')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) or
                Q(email__icontains=search) or
                Q(num_cni__icontains=search) or
                Q(nom_organization__icontains=search) or
                Q(addresse__icontains=search)
            )
        return queryset

    # --- Actions personnalisées ---
    @action(detail=False, methods=['GET'], permission_classes=[IsAdministrateurCadastral])
    def individuals(self, request):
        """Liste des utilisateurs individuels"""
        queryset = self.filter_queryset(self.get_queryset().filter(account_type='IND'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], permission_classes=[IsAdministrateurCadastral])
    def organizations(self, request):
        """Liste des organisations"""
        queryset = self.filter_queryset(self.get_queryset().filter(account_type='ORG'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[IsAdministrateurCadastral])
    def activate(self, request, pk=None):
        """Activer un compte utilisateur"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(
            {'status': 'Compte activé avec succès'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['POST'], permission_classes=[IsAdministrateurCadastral])
    def deactivate(self, request, pk=None):
        """Désactiver un compte utilisateur"""
        user = self.get_object()
        if not user.has_permission(IsSuperAdministrateur)\
        or request.user.has_permission(IsSuperAdministrateur):
            user.is_active = False
        else:
            return HttpResponseForbidden("Vous n'avez pas la permission !")
        user.save()
        
        return Response(
            {'status': 'Compte désactivé avec succès'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['GET'], permission_classes=[IsAdministrateurCadastral])
    def stats(self, request):
        """Statistiques globales des utilisateurs"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'individuals': queryset.filter(account_type='IND').count(),
            'organizations': queryset.filter(account_type='ORG').count(),
            'male': queryset.filter(genre='M').count(),
            'female': queryset.filter(genre='F').count(),
            'domaines': dict(queryset.exclude(domaine__isnull=True)
                           .values_list('domaine')
                           .annotate(count=models.Count('domaine')))
        }
        
        return Response(stats)
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdministrateur])
    def assign_role(self, request, pk=None):
        """
        Attribue un rôle à un utilisateur (accessible uniquement par les superusers)
        Requête POST attendue: {'role': 'nom_du_role'}
        """
        user = self.get_object(pk=pk)
        current_user = request.user

        # Vérifier que l'utilisateur actuel est superuser
        if not current_user.is_superuser:
            return Response(
                {"error": "Seuls les superutilisateurs peuvent attribuer des rôles"},
                status=status.HTTP_403_FORBIDDEN
            )

        role_name = request.data.get('role')
        if not role_name:
            return Response(
                {"error": "Le champ 'role' est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return Response(
                {"error": f"Le rôle '{role_name}' n'existe pas"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ajouter l'utilisateur au groupe (rôle)
        user.groups.add(group)
        user.save()

        return Response(
            {
                "success": f"Rôle '{role_name}' attribué avec succès à {user.email}",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )