from datetime import date
import json
from urllib import request
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
import pytest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

User = get_user_model()

@pytest.mark.django_db
class UserViewSetTestCase(APITestCase):
    """Tests pour le UserViewSet avec authentification JWT"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.client = APIClient()
        
        # Création des groupes/rôles
        self.super_admin_group = Group.objects.create(name='SuperAdministrateur')
        self.admin_cadastral_group = Group.objects.create(name='AdministrateurCadastral')
        self.proprietaire_group = Group.objects.create(name='Proprietaire')
        
        # Création des utilisateurs de test
        self.super_admin = User.objects.create_user(
            username='superadmin',
            email='superadmin@test.com',
            password='testpass123',
            account_type='IND',
            genre='M',
            is_superuser=True,
            is_active=True,
            id_cadastrale='ID123',
        )
        self.super_admin.groups.add(self.super_admin_group)
        
        self.admin_cadastral = User.objects.create_user(
            username='admincadastral',
            email='admin@test.com',
            password='testpass123',
            account_type='IND',
            id_cadastrale='ID124',
            genre='F',
            is_active=True
        )
        self.admin_cadastral.groups.add(self.admin_cadastral_group)
        
        self.proprietaire = User.objects.create_user(
            username='proprietaire',
            email='proprio@test.com',
            password='testpass123',
            account_type='IND',
            genre='M',
            id_cadastrale='ID125',
            is_active=True
        )
        self.proprietaire.groups.add(self.proprietaire_group)
        
        self.user_normal = User.objects.create_user(
            username='usernormal',
            email='user@test.com',
            password='testpass123',
            account_type='ORG',
            nom_organization='Test Org',
            id_cadastrale='ID126',
            is_active=True
        )
        
        # URL de base
        from rest_framework.reverse import reverse

        self.users_url = reverse('user-list')  # Ajustez selon votre configuration d'URLs

    def get_jwt_token(self, user):
        """Génère un token JWT pour un utilisateur"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate_user(self, user):
        """Authentifie un utilisateur avec JWT"""
        token = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_unauthenticated_access_denied(self):
        """Test que l'accès non authentifié est refusé"""
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_authenticated(self):
        """Test de listage des utilisateurs avec authentification"""
        print(self.users_url)
        self.authenticate_user(self.admin_cadastral)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(f"\n==========================\n{response.data}")
        self.assertGreaterEqual(len(response.data), 4)  # Au moins 4 utilisateurs créés

    def test_retrieve_user_authenticated(self):
        """Test de récupération d'un utilisateur spécifique"""
        self.authenticate_user(self.admin_cadastral)
        url = reverse('user-detail', kwargs={'pk': self.user_normal.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_normal.email)

    def test_create_user_admin_cadastral(self):
        """Test de création d'utilisateur par admin cadastral"""
        self.authenticate_user(self.admin_cadastral)
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpassword123',
            'account_type': 'IND',
            'genre': 'M'
        }
        
        response = self.client.post(self.users_url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())

    def test_create_user_super_admin(self):
        """Test de création d'utilisateur par super admin"""
        self.authenticate_user(self.super_admin)
        
        user_data = {
            'username': 'superuser',
            'email': 'superuser@test.com',
            'password': 'superpassword123',
            'account_type': 'ORG',
            'nom_organization': 'Super Org'
        }
        
        response = self.client.post(self.users_url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_forbidden_normal_user(self):
        """Test que les utilisateurs normaux ne peuvent pas créer d'utilisateurs"""
        self.authenticate_user(self.user_normal)
        
        user_data = {
            'username': 'forbidden',
            'email': 'forbidden@test.com',
            'password': 'password123',
            'account_type': 'IND'
        }
        
        response = self.client.post(self.users_url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_admin_cadastral(self):
        """Test de mise à jour d'utilisateur par admin cadastral"""
        self.authenticate_user(self.admin_cadastral)
        
        url = reverse('user-detail', kwargs={'pk': self.user_normal.pk})
        update_data = {
            'username': 'updated_username',
            'email': 'updated@test.com'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la mise à jour
        self.user_normal.refresh_from_db()
        self.assertEqual(self.user_normal.email, 'updated@test.com')

    def test_update_user_forbidden_normal_user(self):
        """Test que les utilisateurs normaux ne peuvent pas modifier d'autres utilisateurs"""
        self.authenticate_user(self.user_normal)
        
        url = reverse('user-detail', kwargs={'pk': self.admin_cadastral.pk})
        update_data = {'username': 'hacked'}
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_admin_cadastral(self):
        """Test de suppression d'utilisateur par admin cadastral"""
        self.authenticate_user(self.admin_cadastral)
        
        # Créer un utilisateur à supprimer
        user_to_delete = User.objects.create_user(
            username='todelete',
            email='delete@test.com',
            password='password123'
        )
        
        url = reverse('user-detail', kwargs={'pk': user_to_delete.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=user_to_delete.pk).exists())

    def test_filter_users_by_account_type(self):
        """Test de filtrage des utilisateurs par type de compte"""
        self.authenticate_user(self.admin_cadastral)
        
        response = self.client.get(self.users_url, {'account_type': 'IND'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Response data:", response.data)

        # Vérifier que tous les résultats sont des individus
        for user in response.data['results']:
            self.assertEqual(user['account_type'], 'IND')

    def test_search_users(self):
        """Test de recherche d'utilisateurs"""
        self.authenticate_user(self.admin_cadastral)
        
        response = self.client.get(self.users_url, {'search': 'test.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_individuals_action(self):
        """Test de l'action personnalisée 'individuals'"""
        self.authenticate_user(self.admin_cadastral)
        
        url = reverse('user-individuals')  # Ajustez selon votre configuration
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que seuls les individus sont retournés
        for user in response.data:
            self.assertEqual(user['account_type'], 'IND')

    def test_organizations_action(self):
        """Test de l'action personnalisée 'organizations'"""
        self.authenticate_user(self.admin_cadastral)
        
        url = reverse('user-organizations')  # Ajustez selon votre configuration
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que seules les organisations sont retournées
        for user in response.data:
            self.assertEqual(user['account_type'], 'ORG')

    def test_activate_user_action(self):
        """Test de l'action d'activation d'utilisateur"""
        # Créer un utilisateur inactif
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@test.com',
            password='password123',
            is_active=False
        )
        
        self.authenticate_user(self.admin_cadastral)
        
        url = reverse('user-activate', kwargs={'pk': inactive_user.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier l'activation
        inactive_user.refresh_from_db()
        self.assertTrue(inactive_user.is_active)

    def test_deactivate_user_action(self):
        """Test de l'action de désactivation d'utilisateur"""
        self.authenticate_user(self.admin_cadastral)
        
        url = reverse('user-deactivate', kwargs={'pk': self.user_normal.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la désactivation
        self.user_normal.refresh_from_db()
        self.assertFalse(self.user_normal.is_active)

    def test_stats_action(self):
        """Test de l'action de statistiques"""
        self.authenticate_user(self.admin_cadastral)
        
        url = reverse('user-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la structure des statistiques
        expected_keys = ['total', 'active', 'individuals', 'organizations', 'male', 'female', 'domaines']
        for key in expected_keys:
            self.assertIn(key, response.data)

    def test_assign_role_super_admin(self):
        """Test d'attribution de rôle par super admin"""
        self.authenticate_user(self.super_admin)
        
        url = reverse('user-assign-role', kwargs={'pk': self.user_normal.pk})
        role_data = {'role': 'Proprietaire'}
        
        response = self.client.post(url, role_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier l'attribution du rôle
        self.assertTrue(self.user_normal.groups.filter(name='Proprietaire').exists())

    def test_assign_role_forbidden_non_super_admin(self):
        """Test que seuls les super admins peuvent attribuer des rôles"""
        self.authenticate_user(self.admin_cadastral)
        
        url = reverse('user-assign-role', kwargs={'pk': self.user_normal.pk})
        role_data = {'role': 'Proprietaire'}
        
        response = self.client.post(url, role_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_nonexistent_role(self):
        """Test d'attribution d'un rôle inexistant"""
        self.authenticate_user(self.super_admin)
        
        url = reverse('user-assign-role', kwargs={'pk': self.user_normal.pk})
        role_data = {'role': 'RoleInexistant'}
        
        response = self.client.post(url, role_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_jwt_token_refresh(self):
        """Test du rafraîchissement de token JWT"""
        refresh = RefreshToken.for_user(self.user_normal)
        
        # Test avec le token d'accès
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test de rafraîchissement (nécessite l'endpoint de refresh)
        refresh_url = reverse('token_refresh')  # Ajustez selon votre configuration
        refresh_data = {'refresh': str(refresh)}
        
        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_jwt_token(self):
        """Test avec un token JWT invalide"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_jwt_token(self):
        """Test avec un token JWT expiré"""
        # Créer un token avec une durée de vie très courte
        refresh = RefreshToken.for_user(self.user_normal)
        expired_token = str(refresh.access_token)
        
        # Manipuler manuellement le token pour le faire expirer
        import jwt
        from django.conf import settings
        from jwt import ExpiredSignatureError
        
        # Décoder le token pour modifier sa date d'expiration
        payload = jwt.decode(expired_token, settings.SECRET_KEY, algorithms=['HS256'], options={'verify_exp': False})
        payload['exp'] = payload['iat'] - 3600  # Expirer il y a 1 heure
        
        # Recréer un token avec la nouvelle payload expirée
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_token}')
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.client.credentials()  # Retirer les credentials

@pytest.mark.django_db
class UserModelTestCase(TestCase):
    """Tests pour le modèle User (si nécessaire)"""

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': "jack",
            'last_name' : "emmanuel",
            'genre' : 'M',
            'date_naissance': date(1999, 2, 12),
            'id_cadastrale' : "ADMIN12332145",
            'addresse' : 'Melen',
            'account_type' : 'IND',
            'num_telephone': '612345678'
        }

    def test_create_user(self):
        """Test de création d'utilisateur basique"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Test de création de superutilisateur"""
        admin = User.objects.create_superuser(**self.user_data)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)