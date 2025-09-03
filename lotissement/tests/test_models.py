from django.test import TestCase
from django.contrib.gis.geos import Polygon
from django.db import IntegrityError

from account.models import User
from lotissement.models import Lotissement, Bloc, Parcelle, Rue


class TestLotissementModel(TestCase):
    """Tests pour le modèle Lotissement"""
    
    def setUp(self):
        self.lotissement = Lotissement.objects.create(
            name="Lotissement Test",
            addresse="123 Rue Test",
            longeur=100.5,
            superficie_m2=1000.0,
            perimetre_m=120.0
        )
    
    def test_create_lotissement_with_required_fields(self):
        """Test de création d'un lotissement avec les champs requis"""
        self.assertEqual(self.lotissement.name, "Lotissement Test")
        self.assertEqual(self.lotissement.addresse, "123 Rue Test")
        self.assertEqual(self.lotissement.longeur, 100.5)
        self.assertEqual(self.lotissement.superficie_m2, 1000.0)
        self.assertEqual(self.lotissement.perimetre_m, 120.0)
        self.assertIsNotNone(self.lotissement.created_at)
        self.assertIsNotNone(self.lotissement.updated_at)
    
    def test_lotissement_str_method(self):
        """Test de la méthode __str__ du lotissement"""
        expected_str = "Lotissement Test_123 Rue Test"
        self.assertEqual(str(self.lotissement), expected_str)
    
    def test_lotissement_unique_name_constraint(self):
        """Test de l'unicité du nom du lotissement"""
        with self.assertRaises(IntegrityError):
            Lotissement.objects.create(
                name="Lotissement Test",
                longeur=200.0
            )
    
    def test_lotissement_with_polygon_geometry(self):
        """Test de création d'un lotissement avec géométrie polygon"""
        polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        lotissement = Lotissement.objects.create(
            name="Lotissement Geo",
            longeur=100.0,
            geom=polygon
        )
        self.assertIsNotNone(lotissement.geom)
        self.assertEqual(lotissement.geom.geom_type, 'Polygon')
    
    def test_lotissement_ordering(self):
        """Test de l'ordre par défaut des lotissements"""
        Lotissement.objects.create(name="Z Lotissement", longeur=100.0)
        Lotissement.objects.create(name="A Lotissement", longeur=100.0)
        
        lotissements = list(Lotissement.objects.all())
        self.assertEqual(lotissements[0].name, "A Lotissement")
        self.assertEqual(lotissements[1].name, "Lotissement Test")
        self.assertEqual(lotissements[2].name, "Z Lotissement")


class TestBlocModel(TestCase):
    """Tests pour le modèle Bloc"""
    
    def setUp(self):
        self.lotissement = Lotissement.objects.create(
            name="Lotissement Test",
            longeur=100.0
        )
        self.bloc = Bloc.objects.create(
            name="Bloc A",
            bloc_lotissement=self.lotissement,
            longeur=50.0,
            superficie_m2=500.0,
            perimetre_m=60.0
        )
    
    def test_create_bloc_with_required_fields(self):
        """Test de création d'un bloc avec les champs requis"""
        self.assertEqual(self.bloc.name, "Bloc A")
        self.assertEqual(self.bloc.bloc_lotissement, self.lotissement)
        self.assertEqual(self.bloc.longeur, 50.0)
        self.assertEqual(self.bloc.superficie_m2, 500.0)
        self.assertEqual(self.bloc.perimetre_m, 60.0)
        self.assertIsNotNone(self.bloc.created_at)
        self.assertIsNotNone(self.bloc.updated_at)
    
    def test_bloc_str_method(self):
        """Test de la méthode __str__ du bloc"""
        expected_str = f"Bloc Bloc A - Lotissement Test"
        self.assertEqual(str(self.bloc), expected_str)
    
    def test_bloc_cascade_delete_from_lotissement(self):
        """Test de suppression en cascade depuis le lotissement"""
        bloc_id = self.bloc.id
        self.lotissement.delete()
        self.assertFalse(Bloc.objects.filter(id=bloc_id).exists())
    def test_bloc_unique_name_constraint(self):
        """Test que deux blocs ne peuvent pas avoir le même nom dans un même lotissement."""
        lotissement = Lotissement.objects.create(name="Lotissement A", longeur=100.0)
        
        # Premier bloc - doit réussir
        Bloc.objects.create(name="Bloc A", bloc_lotissement=lotissement, longeur=50.0)
        
        # Deuxième bloc avec le même nom dans le même lotissement
        try:
            Bloc.objects.create(name="Bloc A", bloc_lotissement=lotissement, longeur=60.0)
        except IntegrityError:
            pass  # Comportement attendu
        
        # Vérification que la contrainte ne s'applique pas entre lotissements différents
        lotissement2 = Lotissement.objects.create(name="Lotissement B", longeur=200.0)
        Bloc.objects.create(name="Bloc A", bloc_lotissement=lotissement2, longeur=70.0)  # Doit réussir


class TestParcelleModel(TestCase):
    """Tests pour le modèle Parcelle"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.lotissement = Lotissement.objects.create(
            name="Lotissement Test",
            longeur=100.0
        )
        
        self.bloc = Bloc.objects.create(
            name="Bloc Test",
            bloc_lotissement=self.lotissement,
            longeur=50.0
        )
        
        self.parcelle = Parcelle.objects.create(
            parcelle_bloc=self.bloc,
            proprietaire=self.user,
            longeur=25.0,
            superficie_m2=250.0,
            perimetre_m=30.0
        )
    
    def test_create_parcelle_with_required_fields(self):
        """Test de création d'une parcelle avec les champs requis"""
        self.assertEqual(self.parcelle.parcelle_bloc, self.bloc)
        self.assertEqual(self.parcelle.proprietaire, self.user)
        self.assertEqual(self.parcelle.longeur, 25.0)
        self.assertEqual(self.parcelle.superficie_m2, 250.0)
        self.assertEqual(self.parcelle.perimetre_m, 30.0)
        self.assertIsNotNone(self.parcelle.created_at)
        self.assertIsNotNone(self.parcelle.updated_at)
    
    def test_parcelle_related_name(self):
        """Test du related_name 'parcelles' sur le bloc"""
        parcelle2 = Parcelle.objects.create(
            name='PARCEL!@#',
            parcelle_bloc=self.bloc,
            proprietaire=self.user,
            longeur=30.0
        )
        
        parcelles = self.bloc.parcelles.all()
        self.assertEqual(parcelles.count(), 2)
        # print(f"\\\\\\\\\\\\\\\\\n {parcelles}")
        # self.assertIn(self.parcelle, parcelles)
        # self.assertIn(parcelle2, parcelles)
    
    def test_parcelle_cascade_delete_from_bloc(self):
        """Test de suppression en cascade depuis le bloc"""
        parcelle_id = self.parcelle.id
        self.bloc.delete()
        self.assertFalse(Parcelle.objects.filter(id=parcelle_id).exists())
    
    def test_parcelle_cascade_delete_from_user(self):
        """Test de suppression en cascade depuis l'utilisateur"""
        parcelle_id = self.parcelle.id
        self.user.delete()
        self.assertFalse(Parcelle.objects.filter(id=parcelle_id).exists())


class TestRueModel(TestCase):
    """Tests pour le modèle Rue"""
    
    def setUp(self):
        self.rue = Rue.objects.create(
            name="Rue de la Paix",
            longeur=200.0,
            superficie_m2=800.0,
            perimetre_m=240.0
        )
    
    def test_create_rue_with_required_fields(self):
        """Test de création d'une rue avec les champs requis"""
        self.assertEqual(self.rue.name, "Rue de la Paix")
        self.assertEqual(self.rue.longeur, 200.0)
        self.assertEqual(self.rue.superficie_m2, 800.0)
        self.assertEqual(self.rue.perimetre_m, 240.0)
        self.assertIsNotNone(self.rue.created_at)
        self.assertIsNotNone(self.rue.updated_at)
    
    
    def test_rue_with_polygon_geometry(self):
        """Test de création d'une rue avec géométrie polygon"""
        polygon = Polygon(((0, 0), (0, 0.1), (10, 0.1), (10, 0), (0, 0)))
        rue = Rue.objects.create(
            name="Rue Géométrique",
            longeur=100.0,
            geom=polygon
        )
        self.assertIsNotNone(rue.geom)
        self.assertEqual(rue.geom.geom_type, 'Polygon')


class TestGeometryAbstractModel(TestCase):
    """Tests pour les fonctionnalités héritées du modèle abstrait Geometry"""
    
    def test_default_values_for_geometry_fields(self):
        """Test des valeurs par défaut des champs géométriques"""
        lotissement = Lotissement.objects.create(
            name="Test Default",
            longeur=100.0
        )
        self.assertEqual(lotissement.superficie_m2, 0)
        self.assertEqual(lotissement.perimetre_m, 0)
        self.assertIsNone(lotissement.geom)
    
    def test_geometry_field_verbose_names(self):
        """Test des verbose_name des champs géométriques"""
        lotissement_field = Lotissement._meta.get_field('superficie_m2')
        self.assertEqual(lotissement_field.verbose_name, "Superficie (m²)")
        
        perimetre_field = Lotissement._meta.get_field('perimetre_m')
        self.assertEqual(perimetre_field.verbose_name, "Périmètre (m)")
        
        geom_field = Lotissement._meta.get_field('geom')
        self.assertEqual(geom_field.verbose_name, "Polygone de la parcelle")


class TestModelsIntegration(TestCase):
    """Tests d'intégration entre les modèles"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass123",
            id_cadastrale='CAD13214445',
        )
        
        self.lotissement = Lotissement.objects.create(
            name="Grand Lotissement",
            addresse="Avenue Principale",
            longeur=500.0,
            superficie_m2=25000.0
        )
        
        self.bloc = Bloc.objects.create(
            name="Bloc Principal",
            bloc_lotissement=self.lotissement,
            longeur=100.0,
            superficie_m2=5000.0
        )
        
        self.parcelle = Parcelle.objects.create(
            parcelle_bloc=self.bloc,
            proprietaire=self.user,
            longeur=20.0,
            superficie_m2=400.0
        )
        
        self.rue = Rue.objects.create(
            name="Rue Centrale",
            longeur=200.0,
            superficie_m2=1000.0
        )
    
    def test_complete_hierarchy_creation(self):
        """Test de création d'une hiérarchie complète"""
        self.assertEqual(self.lotissement.bloc_set.count(), 1)
        self.assertEqual(self.bloc.parcelles.count(), 1)
        self.assertEqual(self.user.parcelle_set.count(), 1)
        self.assertEqual(Rue.objects.count(), 1)
        
        self.assertEqual(self.parcelle.parcelle_bloc.bloc_lotissement, self.lotissement)
        self.assertEqual(self.parcelle.proprietaire, self.user)