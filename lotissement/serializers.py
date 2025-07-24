from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Lotissement, Bloc, Parcelle, Rue, User

class LotissementSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Lotissement
        geo_field = 'geom'
        fields = '__all__'

class BlocSerializer(GeoFeatureModelSerializer):
    lotissement = LotissementSerializer(read_only=True)
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
    bloc = BlocSerializer(read_only=True)
    proprietaire = serializers.StringRelatedField()  # ou utilise un UserSerializer si besoin

    class Meta:
        model = Parcelle
        geo_field = 'geom'
        fields = '__all__'