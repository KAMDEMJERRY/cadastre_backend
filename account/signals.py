# cadastre/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.contrib.auth import get_user_model


@receiver(post_migrate)
def setup_groups_and_permissions(sender, **kwargs):
    # Charger les modèles
    User = get_user_model()
    Parcelle = apps.get_model('lotissement', 'Parcelle')
    Bloc = apps.get_model('lotissement', 'Bloc')
    Rue = apps.get_model('lotissement', 'Rue')

    # Créer les groupes
    group_superuser, _ = Group.objects.get_or_create(name='super_administrateurs')
    group_admin, _ = Group.objects.get_or_create(name='administrateurs_cadastraux')
    group_user, _ = Group.objects.get_or_create(name='proprietaires')

    # Permissions pour les modèles
    user_ct = ContentType.objects.get_for_model(User)
    parcelle_ct = ContentType.objects.get_for_model(Parcelle)
    bloc_ct = ContentType.objects.get_for_model(Bloc)
    rue_ct = ContentType.objects.get_for_model(Rue)

    # Permissions CRUD
    parcelle_perms = Permission.objects.filter(content_type=parcelle_ct)
    bloc_perms = Permission.objects.filter(content_type=bloc_ct)
    rue_perms = Permission.objects.filter(content_type=rue_ct)

    # SUPER UTILISATEURS (toutes les permissions)
    superuser_perms = list(parcelle_perms) + list(bloc_perms) + list(rue_perms) + list(Permission.objects.all())
    group_superuser.permissions.set(superuser_perms)

    # ADMINISTRATEURS CADASTRAUX (CRUD sur , proprietaires, parcelles, blocs, rues + assigner utilisateurs,)
    admin_perms = Permission.objects.filter(
        content_type__in=[user_ct, parcelle_ct, bloc_ct, rue_ct],
        codename__startswith=('add_', 'change_', 'delete_', 'view_')
    )
    group_admin.permissions.set(admin_perms)

    # PROPRIETAIRES (read seulement sur leurs parcelles, + export PDF = permission personnalisée)
    user_perms = Permission.objects.filter(
        content_type=parcelle_ct,
        codename='view_parcelle'
    )

    # Ajouter une permission personnalisée export_pdf_parcelle
    export_perm, _ = Permission.objects.get_or_create(
        codename='export_pdf_parcelle',
        name='Peut exporter la parcelle en PDF',
        content_type=parcelle_ct
    )
    group_user.permissions.set(list(user_perms) + [export_perm])
