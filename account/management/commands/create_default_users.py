from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée des utilisateurs par défaut (admin et utilisateur normal)'

    def handle(self, *args, **options):
        self.stdout.write("👥 Début de la création des utilisateurs...")
        
        # Créer l'utilisateur normal
        try:
            user, created = User.objects.get_or_create(
                email='user@example.com',
                defaults={
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
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Utilisateur normal créé : {user.email}")
                )
                self.stdout.write(
                    self.style.WARNING(f"🔑 Mot de passe : Password123!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Utilisateur {user.email} existe déjà")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur création utilisateur normal : {str(e)}")
            )

        # Créer le super admin
        try:
            admin, created = User.objects.get_or_create(
                email='admin@example.com',
                defaults={
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
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Super admin créé : {admin.email}")
                )
                self.stdout.write(
                    self.style.WARNING(f"🔑 Mot de passe : AdminPassword123!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Super admin {admin.email} existe déjà")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur création super admin : {str(e)}")
            )

        self.stdout.write("✅ Opération terminée.")