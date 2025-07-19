from django.db import models

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)

    id_cadastrale = models.CharField(max_length=50, unique=True)
    cni = models.CharField(max_length=50, unique=True) 
    nom = models.CharField(max_length=150, unique=True)
    prenom = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    type_proprietaire = models.CharField(max_length=50, choices=[
        ('public', 'Public'),
        ('prive', 'Prive'),
    ], default='prive')
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('proprietaire', 'Proprietaire'),
    ], default='proprietaire')
    is_active = models.BooleanField(default=True)
    date_activation = models.DateTimeField(auto_now_add=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
   
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

    @property
    def full_name(self):
        return f"{self.prenom} {self.nom}"    