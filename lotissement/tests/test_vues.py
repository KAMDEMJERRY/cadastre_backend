import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from django.contrib.auth.models import Permission, ContentType, Group
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from unittest.mock import patch

from account.models import User
from lotissement.models import Lotissement, Bloc, Parcelle, Rue

User = get_user_model()


class TestLotissementViewSet(APITestCase):
    """Tests pour LotissementViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.simple_user = User.objects.create_user(
            username='simple_user',
            email='simple@example.com',
            password='testpass123',
            id_cadastrale='CAD656432526'

        )
        self.admin_cadastral = User.objects.create_user(
            username='admin_cadastral',
            email='admin@example.com',
            password='testpass123',
            id_cadastrale='CAD656425626'

        )
        self.superuser = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='testpass123',
            id_cadastrale='CAD6564325626'
        )

        self.sample_polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        self.lotissement = Lotissement.objects.create(
            name='Lotissement Test',
            addresse='123 Rue Test',
            longeur=100.5,
            superficie_m2=1000.0,
            perimetre_m=120.0,
            geom=self.sample_polygon
        )

    def test_list_lotissements_authenticated_user(self):
        """Test de liste des lotissements pour un utilisateur authentifié"""
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('lotissement-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['features']), 1)
        self.assertEqual(response.data['features'][0]['properties']['name'], self.lotissement.name)

    def test_list_lotissements_unauthenticated_user(self):
        """Test de liste des lotissements pour un utilisateur non authentifié"""
        url = reverse('lotissement-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_lotissement_authenticated_user(self):
        """Test de récupération d'un lotissement pour un utilisateur authentifié"""
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('lotissement-detail', kwargs={'pk': self.lotissement.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['properties']['name'], self.lotissement.name)

    @patch('account.models.IsAdministrateurCadastralOrSuperAdmin.has_permission')
    def test_create_lotissement_admin_cadastral(self, mock_permission):
        """Test de création d'un lotissement par un administrateur cadastral"""
        mock_permission.return_value = True
        self.client.force_authenticate(user=self.admin_cadastral)
        url = reverse('lotissement-list')
        
        lotissement_data = {
            'name': 'Nouveau Lotissement',
            'addresse': '456 Avenue Test',
            'longeur': 150.0,
            'superficie_m2': 1500.0,
            'perimetre_m': 180.0
        }
        
        response = self.client.post(url, data=lotissement_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lotissement.objects.count(), 2)
        self.assertEqual(Lotissement.objects.last().name, lotissement_data['name'])

    def test_create_lotissement_simple_user_forbidden(self):
        """Test de création d'un lotissement par un utilisateur simple (interdit)"""
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('lotissement-list')
        
        lotissement_data = {
            'name': 'Lotissement Simple',
            'longeur': 100.0
        }
        
        response = self.client.post(url, data=lotissement_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('account.models.IsAdministrateurCadastralOrSuperAdmin.has_permission')
    def test_update_lotissement_admin_cadastral(self, mock_permission):
        """Test de mise à jour d'un lotissement par un administrateur cadastral"""
        mock_permission.return_value = True
        self.client.force_authenticate(user=self.admin_cadastral)
        url = reverse('lotissement-detail', kwargs={'pk': self.lotissement.pk})
        
        updated_data = {'name': 'Lotissement Modifié', 'longeur': 150.0}
        response = self.client.patch(url, data=updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lotissement.refresh_from_db()
        self.assertEqual(self.lotissement.name, 'Lotissement Modifié')
        self.assertEqual(self.lotissement.longeur, 150.0)

    @patch('account.models.IsAdministrateurCadastralOrSuperAdmin.has_permission')
    def test_delete_lotissement_admin_cadastral(self, mock_permission):
        """Test de suppression d'un lotissement par un administrateur cadastral"""
        mock_permission.return_value = True
        self.client.force_authenticate(user=self.admin_cadastral)
        url = reverse('lotissement-detail', kwargs={'pk': self.lotissement.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lotissement.objects.count(), 0)


class TestBlocViewSet(APITestCase):
    """Tests pour BlocViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.simple_user = User.objects.create_user(
            username='simple_user',
            email='simple@example.com',
            password='testpass123'
        )
        self.admin_cadastral = User.objects.create_user(
            username='admin_cadastral',
            email='admin@example.com',
            password='testpass123',
            id_cadastrale='CAD564564',
        )

        self.sample_polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        self.lotissement = Lotissement.objects.create(
            name='Lotissement Test',
            longeur=100.0,
            geom=self.sample_polygon
        )
        self.bloc = Bloc.objects.create(
            name='Bloc Test',
            bloc_lotissement=self.lotissement,
            longeur=50.0,
            geom=self.sample_polygon
        )

    def test_list_blocs_authenticated_user(self):
        """Test de liste des blocs pour un utilisateur authentifié"""
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('bloc-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['features']), 1)
        self.assertEqual(response.data['features'][0]['properties']['name'], self.bloc.name)

    def test_retrieve_bloc_with_lotissement_data(self):
        """Test de récupération d'un bloc avec les données du lotissement"""
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('bloc-detail', kwargs={'pk': self.bloc.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['properties']['name'], self.bloc.name)
        self.assertIn('bloc_lotissement', response.data['properties'])

    @patch('account.models.IsAdministrateurCadastralOrSuperAdmin.has_permission')
    def test_create_bloc_admin_cadastral(self, mock_permission):
        """Test de création d'un bloc par un administrateur cadastral"""
        mock_permission.return_value = True
        self.client.force_authenticate(user=self.admin_cadastral)
        url = reverse('bloc-list')
        
        bloc_data = {
            "type": "Feature",
            "properties": {
                "name": "Nouveau Bloc",
                "bloc_lotissement": self.lotissement.pk,
                "longeur": 60.0
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [30.0, 10.0]]]
            },  # or actual geometry if required
        }
        
        response = self.client.post(url, data=bloc_data, format='json')
        print(f"================================\n{response.data}\n======================") 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bloc.objects.count(), 2)
        self.assertEqual(Bloc.objects.last().name, bloc_data['properties']['name'])




class TestParcelleViewSet(APITestCase):
    """Tests pour ParcelleViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.simple_user = User.objects.create_user(
            username='simple_user',
            email='simple@example.com',
            password='testpass123',
            id_cadastrale='CAD656432562645'
        )
        self.proprietaire = User.objects.create_user(
            username='proprietaire',
            email='proprietaire@example.com',
            password='testpass123',
            id_cadastrale='CAD65643256234346'
        )
        self.admin_cadastral = User.objects.create_user(
            username='admin_cadastral',
            email='admin@example.com',
            password='testpass123',
            id_cadastrale='CAD656432526'
        )
        self.superuser = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='testpass123',
            id_cadastrale='CAD656434556'
        )

        # Create sample geometry
        self.sample_polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        
        # Create test objects
        self.lotissement = Lotissement.objects.create(
            name='Lotissement Test',
            longeur=100.0,
            geom=self.sample_polygon
        )
        self.bloc = Bloc.objects.create(
            name='Bloc Test',
            bloc_lotissement=self.lotissement,
            longeur=50.0,
            geom=self.sample_polygon
        )
        self.parcelle = Parcelle.objects.create(
            parcelle_bloc=self.bloc,
            proprietaire=self.proprietaire,
            longeur=25.0,
            geom=self.sample_polygon
        )

        # Créer l'admin cadastral avec les bonnes permissions
        self.admin_cadastral = User.objects.create_user(
            username='admincadastral',
            email='admin@cadastral.com',
            password='testpass123',
            id_cadastrale='CAD6563335626'

        )
        
        # Ajouter au groupe AdministrateurCadastral
        admin_group, created = Group.objects.get_or_create(name='AdministrateurCadastral')
        self.admin_cadastral.groups.add(admin_group)
        
        # OU créer et assigner des permissions spécifiques
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission
        
        # Créer des permissions personnalisées si elles n'existent pas
        content_type = ContentType.objects.get_for_model(User)
        
        perm_super_admin, created = Permission.objects.get_or_create(
            codename='IsSuperAdministrateur',
            name='Is Super Administrateur',
            content_type=content_type,
        )
        
        perm_admin_cadastral, created = Permission.objects.get_or_create(
            codename='IsAdministrateurCadastrale',
            name='Is Administrateur Cadastrale',
            content_type=content_type,
        )
        
        # Assigner la permission à l'utilisateur
        self.admin_cadastral.user_permissions.add(perm_admin_cadastral)

    def test_list_parcelles_superuser(self):
        """Test de liste des parcelles pour un superutilisateur"""
        self.client.force_authenticate(user=self.superuser)
        url = reverse('parcelle-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['features']), 1)
        self.assertEqual(response.data['features'][0]['properties']['proprietaire'], self.proprietaire.id)
   
    def test_list_parcelles_proprietaire_own_only(self):
        """Test que le propriétaire ne voit que ses propres parcelles"""
        autre_proprietaire = User.objects.create_user(
            username='autre_proprietaire',
            email='autre@example.com',
            password='testpass123',
            id_cadastrale='CAD6564325626457'
        )
        
        # Utilisez soit 'bloc' soit 'parcelle_bloc' selon votre modèle
        Parcelle.objects.create(
            parcelle_bloc=self.bloc,  # ou bloc=self.bloc
            proprietaire=autre_proprietaire,
            longeur=30.0,
            geom=self.sample_polygon
        )
        
        self.client.force_authenticate(user=self.proprietaire)
        url = reverse('parcelle-list')
        response = self.client.get(url)
        
        # Vérifiez que seul la parcelle du propriétaire est retournée
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['features']), 1)  # Ajustez selon votre implémentation
   
    def test_get_queryset_unauthenticated_user(self):
        """Test que les utilisateurs non authentifiés n'ont accès à aucune parcelle"""
        url = reverse('parcelle-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('account.models.IsAdministrateurCadastralOrSuperAdmin.has_permission')
    def test_create_parcelle_admin_cadastral(self, mock_permission):
        """Test de création d'une parcelle par un administrateur cadastral"""
        mock_permission.return_value = True
        self.client.force_authenticate(user=self.admin_cadastral)
        url = reverse('parcelle-list')

        parcelle_data = {
            "type": "Feature",
            "properties": {
                "parcelle_bloc": self.bloc.pk,
                "proprietaire": self.proprietaire.pk,  # Doit correspondre à un ID existant
                "longeur": 30.0
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
            }
        }
        
        response = self.client.post(url, data=parcelle_data, format='json')
        self.assertEqual(response.status_code, 201)  # Vérifiez le code de statut
 
    def test_create_parcelle_simple_user_forbidden(self):
        """Test de création d'une parcelle par un utilisateur simple (interdit)"""
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('parcelle-list')
        
        parcelle_data = {
            "type": "Feature",
            "properties": {
                "parcelle_bloc": self.bloc.pk,
                "proprietaire": self.proprietaire.pk,
                "longeur": 30.0
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
            }
        }
        
        response = self.client.post(url, data=parcelle_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_parcelle_with_related_data(self):
        """Test de récupération d'une parcelle avec les données relationnelles par un utilisateur lambda"""
        
        # IMPORTANT: Associer la parcelle à l'utilisateur simple
        self.parcelle.proprietaire = self.simple_user
        self.parcelle.save()
        
        # Vérifier que la parcelle existe et appartient à l'utilisateur
        self.assertTrue(Parcelle.objects.filter(pk=self.parcelle.pk, proprietaire=self.simple_user).exists())
        
        # Authentifier l'utilisateur lambda
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('parcelle-detail', kwargs={'pk': self.parcelle.pk})
        
        response = self.client.get(url)
        
        # Debug si nécessaire
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
            print(f"Parcelle proprietaire: {self.parcelle.proprietaire}")
            print(f"Simple user: {self.simple_user}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que les données relationnelles sont présentes
        data = response.data
        self.assertIn('id', data)
        # Ajoutez d'autres vérifications selon votre serializer

    def test_cannot_access_other_user_parcelle(self):
        """Test qu'un utilisateur lambda ne peut pas accéder aux parcelles d'un autre utilisateur"""
        
        # Créer un autre utilisateur
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='testpass123'
        )
        
        # La parcelle appartient à other_user
        self.parcelle.proprietaire = other_user
        self.parcelle.save()
        
        # Authentifier simple_user (qui n'est PAS le propriétaire)
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('parcelle-detail', kwargs={'pk': self.parcelle.pk})
        
        response = self.client.get(url)
        
        # simple_user ne devrait pas pouvoir voir la parcelle d'other_user
        # Le get_queryset() va filtrer et la parcelle ne sera pas trouvée
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_access_all_parcelles(self):
        """Test qu'un admin cadastral peut accéder à toutes les parcelles"""
        
        # Créer un autre utilisateur et lui assigner la parcelle
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='testpass123'
        )
        self.parcelle.proprietaire = other_user
        self.parcelle.save()
        
        # Debug de l'admin cadastral
        print(f"Admin cadastral: {self.admin_cadastral}")
        print(f"Is superuser: {self.admin_cadastral.is_superuser}")
        print(f"Groups: {list(self.admin_cadastral.groups.all())}")
        print(f"User permissions: {list(self.admin_cadastral.user_permissions.all())}")
        print(f"All permissions: {list(self.admin_cadastral.get_all_permissions())}")
        
        # Vérifier les permissions spécifiques
        print(f"Has IsSuperAdministrateur: {self.admin_cadastral.has_perm('account.IsSuperAdministrateur')}")
        print(f"Has IsAdministrateurCadastrale: {self.admin_cadastral.has_perm('account.IsAdministrateurCadastrale')}")
        
        # Vérifier le groupe
        is_in_admin_group = self.admin_cadastral.groups.filter(name='AdministrateurCadastral').exists()
        print(f"Is in AdministrateurCadastral group: {is_in_admin_group}")
        
        # Authentifier avec l'admin cadastral
        self.client.force_authenticate(user=self.admin_cadastral)
        url = reverse('parcelle-detail', kwargs={'pk': self.parcelle.pk})
        
        response = self.client.get(url)
        
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response data: {response.data}")
        
        # L'admin doit pouvoir voir la parcelle même si elle ne lui appartient pas
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# class TestRueViewSet(APITestCase):
#     """Tests pour RueViewSet"""

#     def setUp(self):
#         self.client = APIClient()
#         self.simple_user = User.objects.create_user(
#             username='simple_user',
#             email='simple@example.com',
#             password='testpass123'
#         )
#         self.sample_polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
#         self.rue = Rue.objects.create(
#             name='Rue Test',
#             longeur=200.0,
#             geom=self.sample_polygon
#         )

#     def test_list_rues_with_model_permissions(self):
#         """Test de liste des rues avec les permissions de modèle Django"""
#         content_type = ContentType.objects.get_for_model(Rue)
#         permission = Permission.objects.get(
#             codename='view_rue',
#             content_type=content_type,
#         )
#         self.simple_user.user_permissions.add(permission)
        
#         self.client.force_authenticate(user=self.simple_user)
#         url = reverse('rue-list')
        
#         response = self.client.get(url)
        
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['features']), 1)
#         self.assertEqual(response.data['features'][0]['properties']['name'], self.rue.name)

#     def test_list_rues_without_permissions(self):
#         """Test de liste des rues sans permissions (interdit)"""
#         self.client.force_authenticate(user=self.simple_user)
#         url = reverse('rue-list')
        
#         response = self.client.get(url)
        
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_create_rue_with_permissions(self):
#         """Test de création d'une rue avec les permissions nécessaires"""
#         content_type = ContentType.objects.get_for_model(Rue)
#         add_permission = Permission.objects.get(
#             codename='add_rue',
#             content_type=content_type,
#         )
#         view_permission = Permission.objects.get(
#             codename='view_rue',
#             content_type=content_type,
#         )
#         self.simple_user.user_permissions.add(add_permission)
#         self.simple_user.user_permissions.add(view_permission)
        
#         self.client.force_authenticate(user=self.simple_user)
#         url = reverse('rue-list')
        
#         rue_data = {
#             "type": "Feature",
#             "properties": {
#                 "name": "Nouvelle Rue",
#                 "longeur": 150.0
#             },
#             "geometry": {
#                 "type": "Polygon",
#                 "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
#             }
#         }
        
#         response = self.client.post(url, data=rue_data, format='json')
        
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Rue.objects.count(), 2)
#         self.assertEqual(Rue.objects.last().name, rue_data['properties']['name'])

class TestSerializersIntegration(APITestCase):
    """Tests d'intégration pour les serializers"""

    def setUp(self):
        self.client = APIClient()
        self.simple_user = User.objects.create_user(
            username='simple_user',
            email='simple@example.com',
            password='testpass123'
        )
        self.sample_polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        self.lotissement = Lotissement.objects.create(
            name='Lotissement Test',
            longeur=100.0,
            geom=self.sample_polygon
        )

    def test_lotissement_serializer_geo_format(self):
        """Test que le LotissementSerializer retourne le bon format GeoJSON"""
        self.client.force_authenticate(user=self.simple_user)
        url = reverse('lotissement-detail', kwargs={'pk': self.lotissement.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('type', response.data)
        self.assertIn('geometry', response.data)
        self.assertIn('properties', response.data)
        self.assertEqual(response.data['type'], 'Feature')