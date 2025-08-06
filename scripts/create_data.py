import os, sys
import django
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon

# Configuration du chemin Django
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastre.settings')
django.setup()

from lotissement.models import Lotissement, Bloc, Parcelle

def creer_parcelles_proprietaires():
    """Crée des parcelles pour les utilisateurs ayant le rôle 'proprietaires'"""
    
    # 1. Récupérer tous les propriétaires
    User = get_user_model()
    proprietaires = User.objects.filter(groups__name='proprietaires')
    
    if not proprietaires.exists():
        print("Aucun propriétaire trouvé dans la base de données")
        return
    
    # 2. Créer ou récupérer un lotissement de base
    lotissement, created = Lotissement.objects.get_or_create(
        name="Lotissement Principal",
        defaults={
            'addresse': "Adresse par défaut",
            'description': "Lotissement créé automatiquement",
            'geom': Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))),  # Géométrie carrée simple
            'superficie_m2': 10000,
            'perimetre_m': 400
        }
    )
    
    # 3. Créer ou récupérer un bloc dans ce lotissement
    bloc, created = Bloc.objects.get_or_create(
        name="Bloc A",
        bloc_lotissement=lotissement,
        defaults={
            'description': "Bloc créé automatiquement",
            'geom': Polygon(((0, 0), (0, 0.5), (0.5, 0.5), (0.5, 0), (0, 0))),
            'superficie_m2': 2500,
            'perimetre_m': 200
        }
    )
    
    # 4. Créer des parcelles pour chaque propriétaire
    for i, proprietaire in enumerate(proprietaires, start=1):
        # Coordonnées de base pour la parcelle (à adapter selon vos besoins)
        coords = [
            (0.1, 0.1),
            (0.1, 0.4),
            (0.4, 0.4),
            (0.4, 0.1),
            (0.1, 0.1)
        ]
        
        # Création de la parcelle
        parcelle, created = Parcelle.objects.get_or_create(
            name=f"Parcelle-{proprietaire.id}-{i}",
            parcelle_bloc=bloc,
            proprietaire=proprietaire,
            defaults={
                'geom': Polygon(coords),
                'superficie_m2': 900,
                'perimetre_m': 120
            }
        )
        
        if created:
            print(f"Parcelle {parcelle.name} créée pour {proprietaire.email}")
        else:
            print(f"Parcelle existe déjà pour {proprietaire.email}")

if __name__ == '__main__':
    print("Début de la création des parcelles...")
    creer_parcelles_proprietaires()
    print("Opération terminée.")