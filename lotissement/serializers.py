from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Lotissement, Bloc, Parcelle, Rue, User

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