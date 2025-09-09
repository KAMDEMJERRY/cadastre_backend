from django.db import models
from lotissement.models import Parcelle
# Create your models here.

class Document(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    document = models.TextField()  # Supprime la limitation de longueur
