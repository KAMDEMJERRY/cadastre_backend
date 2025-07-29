from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from unittest.mock import Mock
import datetime

from account.models import User, CustomUserManager, IsSuperAdministrateur, IsAdministrateurCadastral, IsProprietaire

User = get_user_model()

@pytest.mark.django_db
class CustomUserManagerTests(TestCase):
    """Tests pour le CustomUserManager"""
    
    def setUp(self):
        self.manager = CustomUserManager()
        self.manager.model = User
    
    def test_create_user_with_email(self):
        """Test création d'un utilisateur avec email"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            num_cni='123456789',
            addresse='Test Address',
            username='testuser',
            num_telephone='612345678'
        )
        
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_without_email_raises_error(self):
        """Test que la création d'un utilisateur sans email lève une erreur"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email='', password='testpass123')
        
        self.assertEqual(str(context.exception), 'The Email field must be set')
    
    def test_create_user_normalizes_email(self):
        """Test que l'email est normalisé"""
        user = User.objects.create_user(
            email='Test@EXAMPLE.COM',
            password='testpass123',
            num_cni='123456789',
            addresse='Test Address',
            username='testuser',
            num_telephone='612345678'
        )
        
        self.assertEqual(user.email, 'Test@example.com')
    
    def test_create_superuser(self):
        """Test création d'un superutilisateur"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, 'admin@example.com')
        # Vérifier les champs auto-générés
        # self.assertTrue(user.num_cni.startswith('ADMIN_'))
        # self.assertTrue(user.addresse.startswith('ADMIN_'))
        # self.assertTrue(user.username.startswith('ADMIN_'))
    
    def test_create_superuser_with_is_staff_false_raises_error(self):
        """Test que créer un superuser avec is_staff=False lève une erreur"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
        
        self.assertEqual(str(context.exception), 'Superuser must have is_staff=True.')
    
    def test_create_superuser_with_is_superuser_false_raises_error(self):
        """Test que créer un superuser avec is_superuser=False lève une erreur"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )
        
        self.assertEqual(str(context.exception), 'Superuser must have is_superuser=True.')


@pytest.mark.django_db
class UserModelTests(TestCase):
    """Tests pour le modèle User"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'testuser',
            'genre': 'M',
            'date_naissance': datetime.date(1990, 1, 1),
            'id_cadastrale': 'CAD123456',
            'num_cni': '123456789',
            'addresse': 'Test Address',
            'num_telephone': '612345678',
            'account_type': 'IND',
            'domaine': 'Test Domain',
            'nom_organization': None
        }
    
    def test_create_individual_user(self):
        """Test création d'un utilisateur individuel"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.genre, 'M')
        self.assertEqual(user.account_type, 'IND')
        self.assertTrue(user.is_individual())
        self.assertFalse(user.is_organization())
    
    def test_create_organization_user(self):
        """Test création d'un utilisateur organisation"""
        self.user_data.update({
            'account_type': 'ORG',
            'nom_organization': 'Test Organization'
        })
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.account_type, 'ORG')
        self.assertEqual(user.nom_organization, 'Test Organization')
        self.assertTrue(user.is_organization())
        self.assertFalse(user.is_individual())
    
    def test_email_unique_constraint(self):
        """Test que l'email doit être unique"""
        User.objects.create_user(**self.user_data)
        
        # Tenter de créer un autre utilisateur avec le même email
        self.user_data.update({
            'username': 'testuser2',
            'num_cni': '987654321',
            'addresse': 'Another Address',
            'num_telephone': '687654321'
        })
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)
    
    def test_username_unique_constraint(self):
        """Test que le username doit être unique"""
        User.objects.create_user(**self.user_data)
        
        # Tenter de créer un autre utilisateur avec le même username
        self.user_data.update({
            'email': 'test2@example.com',
            'num_cni': '987654321',
            'addresse': 'Another Address',
            'num_telephone': '687654321'
        })
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)
    
    def test_num_cni_unique_constraint(self):
        """Test que le num_cni doit être unique"""
        User.objects.create_user(**self.user_data)
        
        # Tenter de créer un autre utilisateur avec le même num_cni
        self.user_data.update({
            'email': 'test2@example.com',
            'username': 'testuser2',
            'addresse': 'Another Address',
            'num_telephone': '687654321'
        })
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)
    
    def test_addresse_unique_constraint(self):
        """Test que l'adresse doit être unique"""
        User.objects.create_user(**self.user_data)
        
        # Tenter de créer un autre utilisateur avec la même adresse
        self.user_data.update({
            'email': 'test2@example.com',
            'username': 'testuser2',
            'num_cni': '987654321',
            'num_telephone': '687654321'
        })
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)
    
    def test_num_telephone_unique_constraint(self):
        """Test que le num_telephone doit être unique"""
        User.objects.create_user(**self.user_data)
        
        # Tenter de créer un autre utilisateur avec le même numéro
        self.user_data.update({
            'email': 'test2@example.com',
            'username': 'testuser2',
            'num_cni': '987654321',
            'addresse': 'Another Address'
        })
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)
    
    def test_telephone_validation_valid_numbers(self):
        """Test validation des numéros de téléphone valides"""
        valid_numbers = ['612345678', '623456789', '634567890', '645678901']
        
        for i, number in enumerate(valid_numbers):
            self.user_data.update({
                'email': f'test{i}@example.com',
                'username': f'testuser{i}',
                'num_cni': f'12345678{i}',
                'addresse': f'Test Address {i}',
                'num_telephone': number,
                'id_cadastrale': f'CAD{i}-123456'
            })
            
            user = User.objects.create_user(**self.user_data)
            self.assertEqual(user.num_telephone, number)
    
    def test_telephone_validation_invalid_numbers(self):
        """Test validation des numéros de téléphone invalides"""
        invalid_numbers = [
            '512345678',  # Ne commence pas par 6
            '61234567',   # Trop court
            '6123456789', # Trop long
            '6abcdefgh',  # Contient des lettres
            '6123-4567',  # Contient des caractères spéciaux
        ]
        
        for i, number in enumerate(invalid_numbers):
            self.user_data.update({
                'email': f'test{i}@example.com',
                'username': f'testuser{i}',
                'num_cni': f'12345678{i}',
                'addresse': f'Test Address {i}',
                'num_telephone': number
            })
            
            with self.assertRaises(ValidationError):
                user = User(**self.user_data)
                user.full_clean()
    
    def test_genre_choices(self):
        """Test les choix de genre"""
        # Test genre masculin
        user_m = User.objects.create_user(**self.user_data)
        self.assertEqual(user_m.genre, 'M')
        
        # Test genre féminin
        self.user_data.update({
            'email': 'test2@example.com',
            'username': 'testuser2',
            'num_cni': '987654321',
            'addresse': 'Another Address',
            'num_telephone': '687654321',
            'id_cadastrale': f'CAD-123456',
            'genre': 'F'
        })
        user_f = User.objects.create_user(**self.user_data)
        self.assertEqual(user_f.genre, 'F')
    
    def test_account_type_choices(self):
        """Test les choix de type de compte"""
        # Test par défaut (IND)
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.account_type, 'IND')
        
        # Test organisation
        self.user_data.update({
            'email': 'org@example.com',
            'username': 'orguser',
            'num_cni': '987654321',
            'addresse': 'Org Address',
            'num_telephone': '687654321',
            'id_cadastrale': f'CAD-5123456',

            'account_type': 'ORG'
        })
        org_user = User.objects.create_user(**self.user_data)
        self.assertEqual(org_user.account_type, 'ORG')
    
    def test_user_str_method(self):
        """Test la méthode __str__"""
        user = User.objects.create_user(**self.user_data)
        expected_str = f"User: {user.email}"
        self.assertEqual(str(user), expected_str)
    
    def test_is_anonymous_property(self):
        """Test la propriété is_anonymous"""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_anonymous)
    
    def test_is_authenticated_property(self):
        """Test la propriété is_authenticated"""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_authenticated)
    
    def test_username_field_configuration(self):
        """Test que USERNAME_FIELD est configuré sur 'email'"""
        self.assertEqual(User.USERNAME_FIELD, 'email')
    
    def test_required_fields_configuration(self):
        """Test que REQUIRED_FIELDS est vide"""
        self.assertEqual(User.REQUIRED_FIELDS, [])
    
    def test_nullable_fields(self):
        """Test les champs qui peuvent être null"""
        minimal_data = {
            'email': 'minimal@example.com',
            'password': 'testpass123'
        }
        user = User.objects.create_user(**minimal_data)
        
        self.assertIsNone(user.username)
        self.assertIsNone(user.date_naissance)
        self.assertIsNone(user.num_cni)
        self.assertIsNone(user.addresse)
        self.assertIsNone(user.num_telephone)
        self.assertIsNone(user.domaine)
        self.assertIsNone(user.nom_organization)

@pytest.mark.django_db
class PermissionTests(TestCase):
    """Tests pour les classes de permissions personnalisées"""
    
    @classmethod
    def setUpTestData(cls):
        # Créer les groupes une fois pour tous les tests
        cls.super_admin_group, _ = Group.objects.get_or_create(name='super_administrateurs')
        cls.admin_cadastral_group, _ = Group.objects.get_or_create(name='administrateurs_cadastraux')
        cls.proprietaire_group, _ = Group.objects.get_or_create(name='proprietaires')
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = APIView()
        
        # Créer des utilisateurs
        self.super_admin_user = User.objects.create_user(
            email='superadmin@example.com',
            id_cadastrale = "CAD_098768",
            password='testpass123',
            username='superadmin',
            num_cni='111111111',
            addresse='Super Admin Address',
            num_telephone='611111111'
        )
        self.super_admin_user.groups.add(self.super_admin_group)
        
        self.admin_cadastral_user = User.objects.create_user(
            email='admincadastral@example.com',
            id_cadastrale = "CAD_098765",
            password='testpass123',
            username='admincadastral',
            num_cni='222222222',
            addresse='Admin Cadastral Address',
            num_telephone='622222222'
        )
        self.admin_cadastral_user.groups.add(self.admin_cadastral_group)
        
        self.proprietaire_user = User.objects.create_user(
            email='proprietaire@example.com',
            password='testpass123',
            id_cadastrale = "CAD_098769",
            username='proprietaire',
            num_cni='333333333',
            addresse='Proprietaire Address',
            num_telephone='633333333'
        )
        self.proprietaire_user.groups.add(self.proprietaire_group)
        
        self.regular_user = User.objects.create_user(
            email='regular@example.com',
            id_cadastrale = "CAD_0987650",
            password='testpass123',
            username='regular',
            num_cni='444444444',
            addresse='Regular Address',
            num_telephone='644444444'
        )
    
    def test_is_super_administrateur_permission_granted(self):
        """Test que IsSuperAdministrateur accorde la permission aux super administrateurs"""
        request = self.factory.get('/')
        request.user = self.super_admin_user
        
        permission = IsSuperAdministrateur()
        self.assertTrue(permission.has_permission(request, self.view))
    
    def test_is_super_administrateur_permission_denied(self):
        """Test que IsSuperAdministrateur refuse la permission aux non super administrateurs"""
        users_to_test = [self.admin_cadastral_user, self.proprietaire_user, self.regular_user]
        
        for user in users_to_test:
            request = self.factory.get('/')
            request.user = user
            
            permission = IsSuperAdministrateur()
            self.assertFalse(permission.has_permission(request, self.view))
    
    def test_is_administrateur_cadastral_permission_granted(self):
        """Test que IsAdministrateurCadastral accorde la permission aux administrateurs cadastraux"""
        request = self.factory.get('/')
        request.user = self.admin_cadastral_user
        
        permission = IsAdministrateurCadastral()
        self.assertTrue(permission.has_permission(request, self.view))
    
    def test_is_administrateur_cadastral_permission_denied(self):
        """Test que IsAdministrateurCadastral refuse la permission aux non administrateurs cadastraux"""
        users_to_test = [self.super_admin_user, self.proprietaire_user, self.regular_user]
        
        for user in users_to_test:
            request = self.factory.get('/')
            request.user = user
            
            permission = IsAdministrateurCadastral()
            self.assertFalse(permission.has_permission(request, self.view))
    
    def test_is_proprietaire_permission_granted(self):
        """Test que IsProprietaire accorde la permission aux propriétaires"""
        request = self.factory.get('/')
        request.user = self.proprietaire_user
        
        permission = IsProprietaire()
        self.assertTrue(permission.has_permission(request, self.view))
    
    def test_is_proprietaire_permission_denied(self):
        """Test que IsProprietaire refuse la permission aux non propriétaires"""
        users_to_test = [self.super_admin_user, self.admin_cadastral_user, self.regular_user]
        
        for user in users_to_test:
            request = self.factory.get('/')
            request.user = user
            
            permission = IsProprietaire()  # Correction: un seul 'p'
            self.assertFalse(permission.has_permission(request, self.view))
    
    def test_permissions_with_anonymous_user(self):
        """Test que toutes les permissions refusent l'accès aux utilisateurs anonymes"""
        request = self.factory.get('/')
        request.user = Mock()
        request.user.groups.filter.return_value.exists.return_value = False
        
        permissions = [IsSuperAdministrateur(), IsAdministrateurCadastral(), IsProprietaire()]
        
        for permission in permissions:
            self.assertFalse(permission.has_permission(request, self.view))
    
    def test_permissions_with_none_user(self):
        """Test que toutes les permissions gèrent correctement les utilisateurs None"""
        request = self.factory.get('/')
        request.user = None
        
        permissions = [IsSuperAdministrateur(), IsAdministrateurCadastral(), IsProprietaire()]
        
        for permission in permissions:
            self.assertFalse(permission.has_permission(request, self.view))

@pytest.mark.django_db
class UserModelIntegrationTests(TestCase):
    """Tests d'intégration pour le modèle User"""
    
    def test_user_with_multiple_groups(self):
        """Test un utilisateur avec plusieurs groupes"""
        # Créer les groupes
        super_admin_group, _ = Group.objects.get_or_create(name='super_administrateurs')
        admin_cadastral_group, _ = Group.objects.get_or_create(name='administrateurs_cadastraux')
        
        user = User.objects.create_user(
            email='multigroup@example.com',
            password='testpass123',
            username='multigroup',
            num_cni='555555555',
            addresse='Multi Group Address',
            num_telephone='655555555'
        )
        
        # Ajouter l'utilisateur aux deux groupes
        user.groups.add(super_admin_group, admin_cadastral_group)
        
        # Tester les permissions
        request = APIRequestFactory().get('/')
        request.user = user
        
        super_admin_permission = IsSuperAdministrateur()
        admin_cadastral_permission = IsAdministrateurCadastral()
        
        self.assertTrue(super_admin_permission.has_permission(request, APIView()))
        self.assertTrue(admin_cadastral_permission.has_permission(request, APIView()))
    
    def test_complete_user_lifecycle(self):
        """Test complet du cycle de vie d'un utilisateur"""
        # Création
        user = User.objects.create_user(
            email='lifecycle@example.com',
            password='testpass123',
            username='lifecycle',
            genre='F',
            date_naissance=datetime.date(1985, 5, 15),
            id_cadastrale='CAD999999',
            num_cni='999999999',
            addresse='Lifecycle Address',
            num_telephone='699999999',
            account_type='ORG',
            domaine='Technology',
            nom_organization='Lifecycle Org'
        )
        
        # Vérifications initiales
        self.assertTrue(user.is_organization())
        self.assertEqual(user.genre, 'F')
        self.assertEqual(user.domaine, 'Technology')
        
        # Modification
        user.account_type = 'IND'
        user.nom_organization = None
        user.save()
        
        # Vérifications après modification
        user.refresh_from_db()
        self.assertTrue(user.is_individual())
        self.assertIsNone(user.nom_organization)
        
        # Suppression
        user_id = user.id
        user.delete()
        
        # Vérification de la suppression
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)