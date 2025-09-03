#!/bin/bash
echo -e "\033[1;33m🧹 Nettoyage de la base de données de test...\033[0m"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS test_cadastre_db;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "\033[0;32m✅ Base de données de test 'test_cadastre_db' supprimée!\033[0m"
else
    echo -e "\033[0;31m❌ Erreur lors de la suppression\033[0m"
fi
