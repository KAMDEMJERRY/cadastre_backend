

## Configuration pour les developpeurs

## Installation

1. Créer un environnement virtuel dans le repertoire parent:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows

### Cloner le repository
- cd repertoire/parent/
- git clone (url)
- cd projet/

# Definir les variables d'environements
Creer un fichier .env
Copier le contenu de .env.exemple dans le .env
Modifier les valeurs des variables d'environnement

# Installer les dependances
pip install -r requirements.txt


# Installer postgis et etendre postgres pour la gestion des donnees spatiales
chmod +x install_postgis.sh
apt-get update
apt-get install -y postgresql-14-postgis-3 postgresql-14-postgis-3-scripts
./install_postgis.sh

### Créer une branche de suivi pour develop
- git checkout -b  develop origin/develop

### Creer une branche de travaille
- git checkout -b ft/functionalite

