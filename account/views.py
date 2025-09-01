from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import IsAdministrateurCadastral, IsAdministrateurCadastralOrSuperAdmin, IsProprietaire, IsSuperAdministrateur
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Count
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs avec :
    - Gestion des types de compte (Individu/Organisation)
    - Filtres avancés
    - Actions personnalisées
    """

    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'account_type', 
        'genre',
        'is_active',
        'domaine'
    ]
        # Filtrage avancé
    def get_queryset(self):
        queryset = User.objects.all()
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
    # Permissions par action
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        
        elif self.action == 'create':
            # Seuls les admins cadastraux ou superadmins peuvent créer
            return [IsAuthenticated(), IsAdministrateurCadastralOrSuperAdmin()]
        
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Admin cadastraux et superadmins uniquement
            return [IsAuthenticated(), IsAdministrateurCadastralOrSuperAdmin()]
        
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








    def create(self, request, *args, **kwargs):
        print("Données reçues:", request.data)  # Debug
        print("Utilisateur authentifié:", request.user)  # Debug
        
        serializer = self.get_serializer(data=request.data)
        print("Sérialiseur est valide?", serializer.is_valid())  # Debug
        if not serializer.is_valid():
            print("Erreurs de validation:", serializer.errors)  # Debug
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Exception lors de la création:", str(e))  # Debug
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    
def update(self, request, *args, **kwargs):
        # Afficher les données reçues
        print("=" * 50)
        print("MISE À JOUR UTILISATEUR")
        print("=" * 50)
        print("Données reçues:", request.data)
        print("Utilisateur authentifié:", request.user)
        print("ID de l'utilisateur à modifier:", kwargs.get('pk'))
        print("Méthode HTTP:", request.method)
        
        # Récupérer l'instance avant modification
        instance = self.get_object()
        print("Données avant modification:")
        print(f"- Username: {instance.username}")
        print(f"- Email: {instance.email}")
        print(f"- Account Type: {instance.account_type}")
        print(f"- Is Active: {instance.is_active}")
        
        # Validation des données
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        print("Sérialiseur est valide?", serializer.is_valid())
        
        if not serializer.is_valid():
            print("Erreurs de validation:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Effectuer la mise à jour
            self.perform_update(serializer)
            
            # Afficher les données après modification
            print("Mise à jour réussie!")
            print("Données retournées après mise à jour:")
            print(serializer.data)
            
            # Récupérer l'instance fraîche depuis la base pour voir les changements réels
            updated_instance = self.get_object()
            print("Données en base après mise à jour:")
            print(f"- Username: {updated_instance.username}")
            print(f"- Email: {updated_instance.email}")
            print(f"- Account Type: {updated_instance.account_type}")
            print(f"- Is Active: {updated_instance.is_active}")
            
            return Response(serializer.data)
            
        except Exception as e:
            print("Exception lors de la mise à jour:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """Mise à jour partielle avec les mêmes logs"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)









    # --- Actions personnalisées ---
    @action(detail=False, methods=['GET'], permission_classes=[IsAdministrateurCadastral])
    def individuals(self, request):
        """Liste des utilisateurs individuels"""
        queryset = self.filter_queryset(self.get_queryset().filter(account_type='IND'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], permission_classes=[IsAdministrateurCadastralOrSuperAdmin])
    def organizations(self, request):
        """Liste des organisations"""
        queryset = self.filter_queryset(self.get_queryset().filter(account_type='ORG'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[IsAdministrateurCadastralOrSuperAdmin])
    def activate(self, request, pk=None):
        """Activer un compte utilisateur"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(
            {'status': 'Compte activé avec succès'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['POST'], permission_classes=[IsAdministrateurCadastralOrSuperAdmin])
    def deactivate(self, request, pk=None):
        """Désactiver un compte utilisateur"""
        user = self.get_object()
        if not user.groups.filter(name='super_administrateurs')\
        or request.user.has_permission('super_administrateurs'):
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
                           .annotate(count=Count('domaine')))
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdministrateur])
    def assign_role(self, request, pk=None):
        user = self.get_object()
        role_name = request.data.get('role')
        
        if not role_name:
            return Response({"error": "Le champ 'role' est requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return Response({"error": f"Le rôle '{role_name}' n'existe pas"}, status=status.HTTP_404_NOT_FOUND)
        
        user.groups.add(group)
        user.save()

        return Response({
            "success": f"Rôle '{role_name}' attribué avec succès à {user.email}",
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)
            
    @action(detail=False, methods=['get'],permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)