from django.db import models

from account.models import User

# Create your models here.
class Lotissement(models.Model):
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

class Bloc(models.Model):
    name = models.CharField(max_length=100, unique=True)
    lotissement = models.ForeignKey(Lotissement, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Parcelle(models.Model):
    bloc = models.ForeignKey(Bloc, on_delete=models.CASCADE)
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE)
    superficie = models.FloatField(default=0, verbose_name="superficie_m2");
    perimetre = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
