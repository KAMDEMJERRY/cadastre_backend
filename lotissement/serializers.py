from rest_framework import serializers
from .models import Lotissement, Bloc, Parcelle, User

class LotissementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lotissement
        fields = '__all__'

class BlocSerializer(serializers.ModelSerializer):
    lotissement = LotissementSerializer(read_only=True)
    class Meta:
        model = Bloc
        fields = '__all__'

class ParcelleSerializer(serializers.ModelSerializer):
    bloc = BlocSerializer(read_only=True)
    lotissement = LotissementSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Parcelle
        fields = '__all__'
