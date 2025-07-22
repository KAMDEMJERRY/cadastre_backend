

## Configuration pour les developpeurs

## Installation

1. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows

### Cloner le repository
- cd repertoire/parent/
- git clone (url)
- cd projet/

# Installer les dependances
pip install -r requirements.txt

### Créer une branche de suivi pour develop
- git checkout -b  develop origin/develop

# Pour etendre Postgres a Postgis

## Au besoin vous changer le nom de la bd dans le fichier
chmod +x install_postgis.sh
sudo ./install_postgis.sh