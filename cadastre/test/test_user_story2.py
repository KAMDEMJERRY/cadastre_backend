import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from account.models import User
from lotissement.models import Lotissement, Bloc, Parcelle
from django.contrib.gis.geos import Polygon


class CompleteIntegrationTestCase(TestCase):
    """Test d'intégration complet du workflow cadastral"""

    def setUp(self):
        self.client = APIClient()
        
        # Créer les groupes nécessaires
        self.admin_group = Group.objects.get_or_create(name='administrateurs_cadastraux')[0]
        self.proprietaire_group = Group.objects.get_or_create(name='proprietaires')[0]

    def log_response(self, action, response, extra_info=""):
        """Helper pour logger les réponses"""
        print(f"\n{'='*60}")
        print(f"ACTION: {action}")
        print(f"STATUS: {response.status_code}")
        if extra_info:
            print(f"INFO: {extra_info}")
        
        if hasattr(response, 'data') and response.data:
            print(f"RESPONSE DATA:")
            if isinstance(response.data, dict) or isinstance(response.data, list):
                print(json.dumps(response.data, indent=2, default=str))
            else:
                print(response.data)
        print(f"{'='*60}\n")

    def test_complete_cadastral_workflow(self):
        """Test complet du workflow cadastral"""
        
        # ============================================================
        # ÉTAPE 1: Superutilisateur s'authentifie et crée les utilisateurs
        # ============================================================
        
        # Créer et authentifier le superutilisateur
        superuser = User.objects.create_superuser(
            username='superadmin',
            email='super@admin.com',
            password='superpass123',
            id_cadastrale='SUPER001'
        )
         # Vérification debug
        print(f"Is superuser: {superuser.is_superuser}")
        print(f"Groups: {list(superuser.groups.values_list('name', flat=True))}")

        self.client.force_authenticate(user=superuser)
        
        print("PHASE 1: CRÉATION DES UTILISATEURS PAR LE SUPERUTILISATEUR")
        
        # Créer trois utilisateurs simples
        simple_users = []
        for i in range(1, 4):
            user_data = {
                'username': f'user{i}',
                'email': f'user{i}@test.com',
                'password': f'userpass{i}23',
                'account_type': 'IND',
                'genre': 'M' if i % 2 == 1 else 'F',
                'id_cadastrale': f'USER00{i}'
            }
            
            response = self.client.post(reverse('user-list'), user_data, format='json')
            self.log_response(f"Création utilisateur simple {i}", response)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Récupérer l'utilisateur créé
            user = User.objects.get(username=f'user{i}')
            simple_users.append(user)
        
        # Créer un agent cadastral
        agent_data = {
            'username': 'agentcadastral',
            'email': 'agent@cadastral.com',
            'password': 'agentpass123',
            'account_type': 'IND',
            'genre': 'M',
            'id_cadastrale': 'AGENT001'
        }
        
        response = self.client.post(reverse('user-list'), agent_data, format='json')
        self.log_response("Création agent cadastral", response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Récupérer l'agent et l'ajouter au groupe AdministrateurCadastral
        agent_cadastral = User.objects.get(username='agentcadastral')
        agent_cadastral.groups.add(self.admin_group)
        
        # ============================================================
        # ÉTAPE 2: Créer trois lotissements
        # ============================================================
        
        print("\nPHASE 2: CRÉATION DES LOTISSEMENTS")
        
        lotissements = []
        for i in range(1, 4):
            # Géométrie pour le lotissement (polygone)
            coords = [
                [i*10.0, i*10.0], 
                [(i+1)*10.0, i*10.0], 
                [(i+1)*10.0, (i+1)*10.0], 
                [i*10.0, (i+1)*10.0], 
                [i*10.0, i*10.0]
            ]
            
            lotissement_data = {
                'name': f'Lotissement {i}',
                'description': f'Description du lotissement {i}',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [coords]
                },
                'superficie_m2': 1000.0 * i,
                'longeur': 50.0 * i,
                'perimetre_m': 200.0 * i
            }
            
            response = self.client.post(reverse('lotissement-list'), lotissement_data, format='json')
            self.log_response(f"Création lotissement {i}", response)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            lotissement = Lotissement.objects.get(name=f'Lotissement {i}')
            lotissements.append(lotissement)
        
        # ============================================================
        # ÉTAPE 3: Créer trois blocs pour chaque lotissement
        # ============================================================
        
        print("\nPHASE 3: CRÉATION DES BLOCS")
        
        all_blocs = []
        bloc_counter = 1

        for lot in lotissements:
            # Créer 2-3 blocs par lotissement avec géométrie
            for j in range(1, 4):  # 3 blocs par lot
                # Calculer les coordonnées du bloc basées sur le lotissement
                lot_coords = list(lot.geom.coords[0]) if lot.geom else None
                
                if lot_coords:
                    # Diviser le lotissement en blocs
                    min_x = min(coord[0] for coord in lot_coords[:-1])
                    max_x = max(coord[0] for coord in lot_coords[:-1])
                    min_y = min(coord[1] for coord in lot_coords[:-1])
                    max_y = max(coord[1] for coord in lot_coords[:-1])
                    
                    # Créer des blocs côte à côte
                    width = (max_x - min_x) / 3  # Diviser en 3 parties
                    bloc_min_x = min_x + ((j-1) * width)
                    bloc_max_x = min_x + (j * width)
                    
                    bloc_coords = [
                        (bloc_min_x, min_y),
                        (bloc_max_x, min_y),
                        (bloc_max_x, max_y),
                        (bloc_min_x, max_y),
                        (bloc_min_x, min_y)
                    ]
                else:
                    # Géométrie par défaut si le lot n'a pas de géométrie
                    base_x = bloc_counter * 1000
                    base_y = bloc_counter * 1000
                    bloc_coords = [
                        (base_x, base_y),
                        (base_x + 500, base_y),
                        (base_x + 500, base_y + 500),
                        (base_x, base_y + 500),
                        (base_x, base_y)
                    ]
                
                bloc_data = {
                    'name': f'BLOC_{bloc_counter:03d}',
                    'bloc_lotissement': lot.id,
                    'superficie': 2000 + (bloc_counter * 100),
                    'description': f"GPS_BLOC_{bloc_counter}",
                    'geom': {
                        "type": "Polygon",
                        "coordinates": [bloc_coords]
                    }
                }
                
                response = self.client.post(reverse('bloc-list'), bloc_data, format='json')
                self.log_response(f"Création bloc {bloc_counter}", response)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                all_blocs.append(response.data)
                bloc_counter += 1
        
        # ============================================================
        # ÉTAPE 4: L'agent cadastral se connecte
        # ============================================================
        
        print("\nPHASE 4: AUTHENTIFICATION DE L'AGENT CADASTRAL")
        
        self.client.force_authenticate(user=agent_cadastral)
        
        # Vérification des permissions de l'agent
        response = self.client.get(reverse('user-list'))
        self.log_response("Vérification accès agent aux utilisateurs", response, 
                         f"Agent groups: {list(agent_cadastral.groups.all())}")
        
        # ============================================================
        # ÉTAPE 5: L'agent cadastral crée deux parcelles dans deux blocs différents
        # ============================================================

        print("\nPHASE 5: CRÉATION DES PARCELLES PAR L'AGENT")

        # Sélectionner deux blocs différents (premier bloc de lot 1 et deuxième bloc de lot 2)
        bloc1_data = all_blocs[0]  # Premier bloc du premier lotissement
        bloc2_data = all_blocs[4]  # Deuxième bloc du deuxième lotissement

        parcelles = []
        for i, bloc_data in enumerate([bloc1_data, bloc2_data], 1):
            # Récupérer l'objet Bloc depuis la base de données pour accéder à la géométrie
            bloc = Bloc.objects.get(id=bloc_data['id'])  # ou bloc_data['id'] selon votre clé
            
            # Vérifier si la géométrie existe
            if bloc.geom is None:
                # Créer une géométrie par défaut si elle n'existe pas
                # from django.contrib.gis.geos import Polygon
                default_coords = [
                    (i * 1000, i * 1000),
                    (i * 1000 + 500, i * 1000),
                    (i * 1000 + 500, i * 1000 + 500),
                    (i * 1000, i * 1000 + 500),
                    (i * 1000, i * 1000)
                ]
                bloc.geom = Polygon(default_coords)
                bloc.save()
            
            # Maintenant on peut accéder aux coordonnées
            base_coords = list(bloc.geom.coords[0])
            
            # Réduire la taille de la parcelle
            parcelle_coords = [
                [base_coords[0][0] + 50, base_coords[0][1] + 50],      # Décaler de 50 unités
                [base_coords[1][0] - 50, base_coords[1][1] + 50],
                [base_coords[2][0] - 50, base_coords[2][1] - 50],
                [base_coords[3][0] + 50, base_coords[3][1] - 50],
                [base_coords[0][0] + 50, base_coords[0][1] + 50]       # Fermer le polygone
            ]
            
            parcelle_data = {
                'name': f'P00{i}',
                'superficie_m2': 50.0 * i,
                'geom': {
                    'type': 'Polygon',
                    'coordinates': [parcelle_coords]
                },
                'parcelle_bloc': bloc.id,  # ou bloc.id selon votre modèle
                'proprietaire': simple_users[0].id,  # Associer au premier utilisateur simple
                'longeur': 8.0,
                'perimetre_m': 32.0
            }
            
            response = self.client.post(reverse('parcelle-list'), parcelle_data, format='json')
            self.log_response(f"Création parcelle {i}", response, 
                            f"Bloc: {bloc.name}, Propriétaire: {simple_users[0].username}")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            parcelle = Parcelle.objects.get(name=f'P00{i}')
            parcelles.append(parcelle)
        # ============================================================
        # ÉTAPE 6: L'utilisateur se connecte et accède à ses parcelles
        # ============================================================
        
        print("\nPHASE 6: ACCÈS AUX PARCELLES PAR L'UTILISATEUR PROPRIÉTAIRE")
        
        # Authentifier le premier utilisateur simple (propriétaire des parcelles)
        self.client.force_authenticate(user=simple_users[0])
        
        # L'utilisateur accède à la liste de toutes ses parcelles
        response = self.client.get(reverse('parcelle-list'))
        self.log_response("Liste des parcelles du propriétaire", response,
                         f"Utilisateur: {simple_users[0].username}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifications des résultats
        if 'features' in response.data:
            features = response.data['features']
            self.assertEqual(len(features), 2, "L'utilisateur devrait voir exactement 2 parcelles")
            
            # Vérifier que toutes les parcelles appartiennent bien à cet utilisateur
            for feature in features:
                proprietaire_id = feature['properties']['proprietaire']
                self.assertEqual(proprietaire_id, simple_users[0].id)
                print(f"✓ Parcelle {feature['properties']['name']} appartient bien à {simple_users[0].username}")
        
        # ============================================================
        # ÉTAPE 7: Tests supplémentaires - Accès détaillé aux parcelles
        # ============================================================
        
        print("\nPHASE 7: ACCÈS DÉTAILLÉ AUX PARCELLES")
        
        # Accéder à chaque parcelle individuellement
        for parcelle in parcelles:
            response = self.client.get(reverse('parcelle-detail', kwargs={'pk': parcelle.pk}))
            self.log_response(f"Détail parcelle {parcelle.name}", response)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # ============================================================
        # ÉTAPE 8: Test d'isolation - Un autre utilisateur ne peut pas voir ces parcelles
        # ============================================================
        
        print("\nPHASE 8: TEST D'ISOLATION DES DONNÉES")
        
        # Authentifier le deuxième utilisateur simple
        self.client.force_authenticate(user=simple_users[1])
        
        response = self.client.get(reverse('parcelle-list'))
        self.log_response("Liste des parcelles du 2ème utilisateur (doit être vide)", response,
                         f"Utilisateur: {simple_users[1].username}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'features' in response.data:
            self.assertEqual(len(response.data['features']), 0, 
                           "Le 2ème utilisateur ne devrait voir aucune parcelle")
        
        # Tenter d'accéder à une parcelle spécifique (devrait échouer)
        response = self.client.get(reverse('parcelle-detail', kwargs={'pk': parcelles[0].pk}))
        self.log_response("Tentative d'accès à une parcelle d'un autre utilisateur", response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        print("\n" + "="*80)
        print("TEST D'INTÉGRATION COMPLET TERMINÉ AVEC SUCCÈS!")
        print("="*80)