from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'id_cadastrale', 'cni', 'nom', 'prenom', 'email',
            'type_proprietaire', 'role', 'is_active', 'full_name',
            'date_activation', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_activation', 'date_creation', 'date_modification']

    def validate_email(self, value):
        """Validation personnalisée de l'email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_cni(self, value):
        """Validation personnalisée du CNI"""
        if len(value) < 5:
            raise serializers.ValidationError("Le CNI doit contenir au moins 5 caractères.")
        return value

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id_cadastrale', 'cni', 'nom', 'prenom', 'email',
            'type_proprietaire', 'role', 'is_active'
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'nom', 'prenom', 'email', 'type_proprietaire', 
            'role', 'is_active'
        ]