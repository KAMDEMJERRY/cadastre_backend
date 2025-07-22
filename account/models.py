from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from rest_framework.permissions import BasePermission

>>>>>>> Stashed changes

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 50, blank = True, null = True, unique = True)
    email = models.EmailField('email address', unique = True)

    genre = models.CharField('Genre', max_length=10, choices=[('M', 'Male'), ('F', 'Female')], default='M')
    date_naissance = models.DateField(blank=True, null=True)
    id_cadastrale = models.CharField(max_length=50, unique=True)
    num_cni = models.CharField(max_length=50, unique=True)
    addresse = models.CharField(max_length=50, unique=True)
    num_tel_regex = RegexValidator(regex=r'^6\d{8}$', message="Le numéro doit contenir exactement 9 chiffres et commencer par 6.")
    num_telephone = models.CharField('Telephone', max_length=9, validators=[num_tel_regex] , unique=True)
    
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
    # Champs spécifiques aux organisations (optionnels)
    nom_organization = models.CharField(max_length=100, blank=True, null=True)   
    
    def is_individual(self):
        return self.account_type == self.INDIVIDU

    def is_organization(self):
        return self.account_type == self.ORGANISATION

    def __str__(self):
        return f"\n[Prenom : {self.prenom}\n\
                    Nom : {self.nom}\n\
                    Email : ({self.email})]\n"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    





class IsSuperAdministrateur(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='super_administrateurs').exists()

class IsAdministrateurCadastral(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='administrateurs_cadastraux').exists()

class IsProprietaire(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='proprietaires').exists()
