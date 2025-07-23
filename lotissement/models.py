from django.db import models
from django.contrib.gis.db import models as gis_models

from account.models import User

class Geometry(models.Model):
    longeur = models.FloatField()
    superficie_m2 = models.FloatField(default=0, verbose_name="Superficie (m²)")
    perimetre_m = models.FloatField(default=0, verbose_name="Périmètre (m)")
    geom = gis_models.PolygonField(srid=4326, verbose_name="Polygone de la parcelle")
    
    class Meta:
        abstract: True
    
# Create your models here.
class Lotissement(Geometry):
    name = models.CharField(max_length=100, unique=True)
    addresse = models.CharField(null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + "_" + self.addresse 

    class Meta:
        verbose_name = "Lotissement"
        verbose_name_plural = "Lotissements"
        ordering = ['name']

class Bloc(Geometry):
    name = models.CharField(max_length=100, unique=True)
    bloc_lotissement = models.ForeignKey(Lotissement, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
      return f"Bloc {self.name} - {self.lotissement.name}"

class Parcelle(Geometry):
    parcelle_bloc = models.ForeignKey(Bloc, on_delete=models.CASCADE, related_name='parcelles')
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Rue(Geometry):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Ajoutez ceci
    updated_at = models.DateTimeField(auto_now=True)      