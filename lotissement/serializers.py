from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Lotissement, Bloc, Parcelle, Rue, User
from django.db.models import Count
class LotissementSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Lotissement
        geo_field = 'geom'
        fields = '__all__'

class BlocSerializer(GeoFeatureModelSerializer):
    bloc_lotissement = serializers.PrimaryKeyRelatedField(queryset=Lotissement.objects.all())
    class Meta:
        model = Bloc
        geo_field = 'geom'
        fields = '__all__'

class RueSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Rue
        geo_field = 'geom'
        fields = '__all__'


class ParcelleSerializer(GeoFeatureModelSerializer):
    bloc = serializers.PrimaryKeyRelatedField(source='parcelle_bloc', read_only=True)
    proprietaire = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True  # S'assure que le champ est obligatoire
    ) # ou utilise un UserSerializer si besoin

    class Meta:
        model = Parcelle
        geo_field = 'geom'
        fields = '__all__'
        
        

class LotissementStatsSerializer(serializers.ModelSerializer):
    nombre_blocs = serializers.IntegerField(read_only=True)
    nombre_parcelles = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Lotissement
        fields = [
            'id', 'name', 'addresse', 'description',
            'superficie_m2', 'perimetre_m',
            'nombre_blocs', 'nombre_parcelles',
            'created_at', 'updated_at'
        ]

class BlocStatsSerializer(serializers.ModelSerializer):
    nombre_parcelles = serializers.IntegerField(read_only=True)
    lotissement_nom = serializers.CharField(source='bloc_lotissement.name', read_only=True)
    
    class Meta:
        model = Bloc
        fields = [
            'id', 'name', 'lotissement_nom',
            'superficie_m2', 'perimetre_m',
            'nombre_parcelles', 'description',
            'created_at', 'updated_at'
        ]

class LotissementDetailSerializer(serializers.ModelSerializer):
    blocs_count = serializers.IntegerField(read_only=True)
    parcelles_count = serializers.IntegerField(read_only=True)
    blocs = serializers.SerializerMethodField()
    
    class Meta:
        model = Lotissement
        fields = [
            'id', 'name', 'addresse', 'description',
            'superficie_m2', 'perimetre_m', 'geom',
            'blocs_count', 'parcelles_count', 'blocs',
            'created_at', 'updated_at'
        ]
    
    def get_blocs(self, obj):
        blocs = Bloc.objects.filter(bloc_lotissement=obj).annotate(
            parcelles_count=Count('parcelles')
        )
        from .serializers import BlocStatsSerializer
        return BlocStatsSerializer(blocs, many=True).data