#!/bin/bash
echo -e "\033[0;34m🧪 Exécution des tests...\033[0m"

# Vérifier si la base de données de test existe
if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw test_cadastre_db; then
    echo -e "\033[1;33m⚠️  Base de données de test non trouvée, création...\033[0m"
    ./setup_test_db.sh
fi

# Exécuter les tests
echo -e "\033[0;34m🚀 Lancement des tests Django...\033[0m"
pytest $*

# Afficher le statut
if [ $? -eq 0 ]; then
    echo -e "\033[0;32m✅ Tous les tests sont passés!\033[0m"
else
    echo -e "\033[0;31m❌ Certains tests ont échoué\033[0m"
fi
