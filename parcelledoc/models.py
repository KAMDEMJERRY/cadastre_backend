from django.db import models
from lotissement.models import Parcelle
# Create your models here.

class Document(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    document = models.CharField(max_length=100);
