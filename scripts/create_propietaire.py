import os
import sys
import django
import random


# Configuration initiale
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastre.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Polygon
from faker import Faker

from lotissement.models import Lotissement, Bloc, Parcelle

fake = Faker()
User = get_user_model()
def creer_utilisateurs_proprietaires():
    """Crée 3 utilisateurs avec le rôle propriétaire"""
    groupe_proprietaire, _ = Group.objects.get_or_create(name='proprietaires')
    proprietaires = []
    
    for i in range(1, 4):
        email = f'proprietaire{i}@example.com'
        user = User.objects.create_user(
            email=email,
            password='Password123!',
            username=f'proprietaire{i}',
            num_telephone=f'6{random.randint(10000000, 99999999)}',
            addresse=fake.address(),
            num_cni=f'CNI{random.randint(100000, 999999)}',
            id_cadastrale=f'CAD-PROP-{i}-{random.randint(1000, 9999)}',
            account_type='IND'
        )
        user.groups.add(groupe_proprietaire)
        proprietaires.append(user)
        print(f'Propriétaire créé : {email}')
    
    return proprietaires

def creer_lotissements():
    """Crée 4 lotissements avec des géométries aléatoires"""
    lotissements = []
    for i in range(1, 5):
        coords = [(random.uniform(0, 1), random.uniform(0, 1)) for _ in range(4)]
        coords.append(coords[0])  # Fermer le polygone
        
        lotissement = Lotissement.objects.create(
            name=f'Lotissement {i}',
            addresse=fake.address(),
            description=f'Lotissement créé automatique #{i}',
            geom=Polygon(coords),
            superficie_m2=random.uniform(5000, 20000),
            perimetre_m=random.uniform(500, 1500)
        )
        lotissements.append(lotissement)
        print(f'Lotissement créé : {lotissement.name}')
    
    return lotissements

def creer_blocs(lotissements):
    """Crée 7 blocs répartis sur les 4 lotissements"""
    blocs = []
    for i in range(1, 8):
        lotissement = random.choice(lotissements)
        coords = [(random.uniform(0, 1), random.uniform(0, 1)) for _ in range(4)]
        coords.append(coords[0])  # Fermer le polygone
        
        bloc = Bloc.objects.create(
            name=f'Bloc {chr(64+i)}',  # A, B, C...
            bloc_lotissement=lotissement,
            description=f'Bloc {chr(64+i)} du {lotissement.name}',
            geom=Polygon(coords),
            superficie_m2=random.uniform(1000, 5000),
            perimetre_m=random.uniform(200, 800)
        )
        blocs.append(bloc)
        print(f'Bloc créé : {bloc.name} ({lotissement.name})')
    
    return blocs

def creer_parcelles(proprietaires, blocs):
    """Crée des parcelles pour chaque propriétaire (3, 2, 5)"""
    parcelles_par_proprietaire = [3, 2, 5]
    
    for i, proprietaire in enumerate(proprietaires):
        for j in range(parcelles_par_proprietaire[i]):
            bloc = random.choice(blocs)
            coords = [(random.uniform(0, 1), random.uniform(0, 1)) for _ in range(4)]
            coords.append(coords[0])  # Fermer le polygone
            
            parcelle = Parcelle.objects.create(
                name=f'Parcelle-{proprietaire.username}-{j+1}',
                parcelle_bloc=bloc,
                proprietaire=proprietaire,
                geom=Polygon(coords),
                superficie_m2=random.uniform(100, 1000),
                perimetre_m=random.uniform(40, 200)
            )
            print(f'Parcelle créée : {parcelle.name} pour {proprietaire.email} dans {bloc.name}')

def main():
    print("### Création des utilisateurs propriétaires ###")
    proprietaires = creer_utilisateurs_proprietaires()
    
    print("\n### Création des lotissements ###")
    lotissements = creer_lotissements()
    
    print("\n### Création des blocs ###")
    blocs = creer_blocs(lotissements)
    
    print("\n### Création et assignation des parcelles ###")
    creer_parcelles(proprietaires, blocs)
    
    print("\nOpération terminée avec succès!")

if __name__ == '__main__':
    main()



# Fonctionnalités du script :

#     Création des utilisateurs :

#         3 propriétaires avec des données réalistes (faker)

#         Chacun ajouté au groupe 'proprietaires'

#     Création des lotissements :

#         4 lotissements avec géométries aléatoires

#         Adresses et descriptions réalistes

#     Création des blocs :

#         7 blocs répartis aléatoirement dans les lotissements

#         Nommés de A à G

#     Création des parcelles :

#         Répartition comme demandé (3, 2, 5 parcelles)

#         Assignation aléatoire aux blocs existants

#         Géométries aléatoires dans les blocs