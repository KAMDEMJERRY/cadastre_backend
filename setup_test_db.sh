#!/bin/bash
# setup_test_db.sh

# Configuration - Modifiez ces valeurs selon votre configuration
DB_NAME="test_cadastre_db"
DB_PASSWORD="jerry"
DB_USER="jerry"  # Remplacez par votre nom d'utilisateur PostgreSQL
DB_HOST="localhost"
DB_PORT="5432"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Configuration de la base de données de test PostGIS...${NC}"

# Vérifier si PostgreSQL est en cours d'exécution
if ! pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
    echo -e "${RED}❌ Erreur: PostgreSQL n'est pas en cours d'exécution sur $DB_HOST:$DB_PORT${NC}"
    echo -e "${YELLOW}💡 Démarrez PostgreSQL avec: sudo systemctl start postgresql${NC}"
    exit 1
fi

# Vérifier si l'utilisateur existe
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo -e "${RED}❌ Erreur: L'utilisateur '$DB_USER' n'existe pas${NC}"
    echo -e "${YELLOW}💡 Créez l'utilisateur avec: sudo -u postgres createuser -d -r -s $DB_USER${NC}"
    exit 1
fi

# Fonction pour exécuter des commandes SQL en tant que postgres
execute_as_postgres() {
    sudo -u postgres psql -c "$1" 2>/dev/null
}

# Fonction pour exécuter des commandes SQL sur une base spécifique
execute_on_db() {
    sudo -u postgres psql -d "$1" -c "$2" 2>/dev/null
}

# 1. Créer la base de données de test si elle n'existe pas
echo -e "${BLUE}📊 Création de la base de données de test...${NC}"

# Supprimer la base existante si elle existe
if execute_as_postgres "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1; then
    echo -e "${YELLOW}⚠️  Base de données existante détectée, suppression...${NC}"
    execute_as_postgres "DROP DATABASE IF EXISTS $DB_NAME;"
fi

# Créer la nouvelle base
if execute_as_postgres "CREATE DATABASE $DB_NAME OWNER $DB_USER;"; then
    echo -e "${GREEN}✅ Base de données '$DB_NAME' créée avec succès${NC}"
else
    echo -e "${RED}❌ Erreur lors de la création de la base de données${NC}"
    exit 1
fi

# 2. Installer les extensions PostGIS
echo -e "${BLUE}🗺️  Installation des extensions PostGIS...${NC}"

extensions=("postgis" "postgis_topology" "fuzzystrmatch" "postgis_tiger_geocoder")
for ext in "${extensions[@]}"; do
    if execute_on_db "$DB_NAME" "CREATE EXTENSION IF NOT EXISTS $ext;"; then
        echo -e "${GREEN}✅ Extension '$ext' installée${NC}"
    else
        echo -e "${YELLOW}⚠️  L'extension '$ext' pourrait ne pas être disponible${NC}"
    fi
done

# 3. Accorder les privilèges nécessaires
echo -e "${BLUE}🔐 Configuration des privilèges...${NC}"

privileges_commands=(
    "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    "GRANT ALL ON SCHEMA public TO $DB_USER;"
    "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
    "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
    "ALTER USER $DB_USER CREATEDB;"
)

for cmd in "${privileges_commands[@]}"; do
    if execute_on_db "$DB_NAME" "$cmd"; then
        echo -e "${GREEN}✅ Privilège accordé${NC}"
    else
        echo -e "${YELLOW}⚠️  Erreur avec: $cmd${NC}"
    fi
done

# 4. Privilèges spéciaux pour PostGIS
echo -e "${BLUE}🌍 Configuration des privilèges PostGIS...${NC}"
execute_on_db "$DB_NAME" "GRANT SELECT, INSERT, UPDATE, DELETE ON spatial_ref_sys TO $DB_USER;"

# 5. Tester la configuration
echo -e "${BLUE}🧪 Test de la configuration...${NC}"
if execute_on_db "$DB_NAME" "SELECT postgis_version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostGIS fonctionne correctement${NC}"
else
    echo -e "${RED}❌ Problème avec PostGIS${NC}"
fi

echo -e "${GREEN}✅ Base de données de test configurée avec succès!${NC}"
echo -e "${BLUE}🚀 Vous pouvez maintenant exécuter vos tests avec :${NC}"
echo -e "${YELLOW}   python manage.py test${NC}"
echo -e "${YELLOW}   python manage.py test your_app.tests.test_models${NC}"

# Créer le script de nettoyage
echo -e "${BLUE}📄 Création du script de nettoyage...${NC}"
cat > cleanup_test_db.sh << EOF
#!/bin/bash
echo -e "${YELLOW}🧹 Nettoyage de la base de données de test...${NC}"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null
if [ \$? -eq 0 ]; then
    echo -e "${GREEN}✅ Base de données de test '$DB_NAME' supprimée!${NC}"
else
    echo -e "${RED}❌ Erreur lors de la suppression${NC}"
fi
EOF

chmod +x cleanup_test_db.sh
echo -e "${GREEN}📄 Script de nettoyage créé : ${YELLOW}cleanup_test_db.sh${NC}"

# Créer le script de test rapide
echo -e "${BLUE}📄 Création du script de test rapide...${NC}"
cat > run_tests.sh << EOF
#!/bin/bash
echo -e "${BLUE}🧪 Exécution des tests...${NC}"

# Vérifier si la base de données de test existe
if ! sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}⚠️  Base de données de test non trouvée, création...${NC}"
    ./setup_test_db.sh
fi

# Exécuter les tests
echo -e "${BLUE}🚀 Lancement des tests Django...${NC}"
pytest \$*

# Afficher le statut
if [ \$? -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les tests sont passés!${NC}"
else
    echo -e "${RED}❌ Certains tests ont échoué${NC}"
fi
EOF

chmod +x run_tests.sh
echo -e "${GREEN}📄 Script de test créé : ${YELLOW}run_tests.sh${NC}"

echo -e "${GREEN}🎉 Configuration terminée!${NC}"