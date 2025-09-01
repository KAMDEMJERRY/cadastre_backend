import os
import django
from datetime import date
import sys

# Configuration du chemin Django
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cadastre.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def create_regular_user():
    """Crée un utilisateur normal avec gestion des erreurs"""
    try:
        user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'password': 'Password123!',
                'num_telephone': '677889900',
                'addresse': '123 Rue Principale, Ville',
                'genre': 'M',
                'username': 'utilisateur_normal',
                'date_naissance': date(1990, 5, 15),
                'num_cni': '1234567890AB',
                'id_cadastrale': 'CAD123456789',
                'account_type': 'IND'
            }
        )
        if created:
            user.set_password('Password123!')
            user.save()
            print(f"✅ Utilisateur normal créé : {user.email}")
        else:
            print(f"⚠️ Utilisateur {user.email} existe déjà")
    except Exception as e:
        print(f"❌ Erreur création utilisateur normal : {str(e)}")

def create_super_admin():
    """Crée un super administrateur avec gestion des erreurs"""
    try:
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'password': 'AdminPassword123!',
                'num_telephone': '699887766',
                'addresse': 'Siège Administratif',
                'genre': 'M',
                'username': 'super_admin',
                'account_type': 'ORG',
                'nom_organization': 'Administration Système',
                'domaine': 'Informatique',
                'num_cni': 'ADMIN_CNI_001',
                'id_cadastrale': 'ADMIN_CAD_001',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin.set_password('AdminPassword123!')
            admin.save()
            
            # Gestion des groupes
            admin_group, _ = Group.objects.get_or_create(name='super_administrateurs')
            admin.groups.add(admin_group)
            
            print(f"✅ Super admin créé : {admin.email}")
        else:
            print(f"⚠️ Super admin {admin.email} existe déjà")
    except Exception as e:
        print(f"❌ Erreur création super admin : {str(e)}")

if __name__ == '__main__':
    print("\nDébut de la création des utilisateurs...")
    create_regular_user()
    create_super_admin()
    print("Opération terminée.\n")