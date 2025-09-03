

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

###################################################

## Configuration pour les tests


### 1. Modifier le script _setup_test_db.sh_ 
DB_USER="votre_nom_utilisateur_postgresql"  # Remplacez par votre utilisateur

### 2. Rendre le script executable et l'executer
- Rendre exécutable
chmod +x setup_test_db.sh

- Exécuter le script
./setup_test_db.sh

### 3. Executer les tests

``` bash

# Méthode 1 : Avec le script automatique
./run_tests.sh

# Méthode 2 : Directement avec Django
python manage.py test --settings=cadastre.settings_test

# Méthode 3 : Tests spécifiques
python manage.py test your_app.tests.test_models --settings=cadastre.settings_test

# Méthode 4 : Tests avec verbosité
python manage.py test --settings=cadastre.settings_test --verbosity=2 

```

### 4 Nettoyer apres les tests(optionnel)
```bash
# Supprimer la base de données de test
./cleanup_test_db.sh 
```