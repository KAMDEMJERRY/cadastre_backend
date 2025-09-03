from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from rest_framework.permissions import BasePermission

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import Group

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Configuration des champs par défaut pour le superutilisateur
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Valeurs par défaut pour les champs obligatoires
        default_username = f'admin_{email.split("@")[0]}'
        extra_fields.setdefault('username', default_username)
        extra_fields.setdefault('num_cni', f'ADMIN_CNI_{email[:5].upper()}')
        extra_fields.setdefault('addresse', 'Adresse administrative')
        extra_fields.setdefault('num_telephone', '000000000')

        # Validation des champs requis pour un superutilisateur
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Création de l'utilisateur
        user = self.create_user(email, password, **extra_fields)
        
        # Association au groupe super_administrateurs
        try:
            admin_group = Group.objects.get(name='super_administrateurs')
            user.groups.add(admin_group)
        except Group.DoesNotExist:
            raise ValueError("Le groupe 'super_administrateurs' n'existe pas. Veuillez le créer d'abord.")

        return user
class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, blank=True, null=True, unique=False)
    email = models.EmailField('email address', unique=True)

    genre = models.CharField('Genre', max_length=10, choices=[('M', 'Male'), ('F', 'Female')], default='M')
    date_naissance = models.DateField(blank=True, null=True)
    id_cadastrale = models.CharField(max_length=50, unique=True, blank=False)
    num_cni = models.CharField(max_length=50, unique=True, null=True, blank=True)
    addresse = models.CharField(max_length=50, unique=False, null=True)
    num_tel_regex = RegexValidator(regex=r'^6\d{8}$', message="Le numéro doit contenir exactement 9 chiffres et commencer par 6.")
    num_telephone = models.CharField('Telephone', max_length=9, validators=[num_tel_regex], unique=True, null=True)
    
    ACCOUNT_TYPE_CHOICES = [
        ('IND', 'Individu'),
        ('ORG', 'Organisation'),
    ]
    account_type = models.CharField(
        max_length=12,
        choices=ACCOUNT_TYPE_CHOICES,
        default='IND',
        verbose_name="Type de compte"
    )

    domaine = models.CharField(max_length=100, blank=True, null=True)
    nom_organization = models.CharField(max_length=100, blank=True, null=True)   
    
    def is_individual(self):
        return self.account_type == 'IND'

    def is_organization(self):
        return self.account_type == 'ORG'

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
    
    def __str__(self):
        return f"User: {self.email}"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
class IsSuperAdministrateur(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.groups.filter(name='super_administrateurs').exists() or request.user.is_superuser)

class IsAdministrateurCadastral(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='administrateurs_cadastraux').exists()
    
class IsProprietaire(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='proprietaires').exists()


class IsAdministrateurCadastralOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and (
            user.groups.filter(name='administrateurs_cadastraux').exists() or
            user.groups.filter(name='super_administrateurs').exists() or
            user.is_superuser  # Ajout de cette condition pour être sûr
        )

