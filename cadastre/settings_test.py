# settings_test.py
import sys
from .settings import *
import os
from decouple import Config, RepositoryEnv

# Chemin vers votre fichier .env personnalisé
ENV_FILE = ".env.test"  # ou ".env.dev", etc.

# Créer une configuration basée sur le fichier spécifié
config = Config(RepositoryEnv(ENV_FILE))

SWAGGER_USE_COMPAT_RENDERERS = False

# Configuration de la base de données pour les tests
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'test_cadastre_db',  # Base créée par le script
        'USER': config('DB_USER'),  # Remplacez par votre utilisateur
        'PASSWORD': config('DB_PASSWORD'),  # Votre mot de passe
        'HOST': config('DB_HOST', 'localhost'),
        'PORT': config('DB_PORT', '5432'),
        'TEST': {
            'NAME': 'test_cadastre_db',
            'CREATE_DB': False,  # La base est déjà créée par le script
        }
    }
}

# Optimisations pour accélérer les tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Cache en mémoire pour les tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Désactiver les migrations pour accélérer les tests (optionnel)
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# Décommentez la ligne suivante si vous voulez désactiver les migrations
# MIGRATION_MODULES = DisableMigrations()

# Logging minimal pour les tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
        },
    },
}

# Configuration pour les tests en parallèle (optionnel)
if 'test' in sys.argv:
    # Utiliser une base de données différente pour chaque processus
    import multiprocessing
    DATABASES['default']['NAME'] = f"test_cadastre_db_{multiprocessing.current_process().name}"