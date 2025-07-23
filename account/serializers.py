from rest_framework import serializers
from .models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    genre_display = serializers.CharField(source='get_genre_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'genre', 'genre_display', 'date_naissance',
            'id_cadastrale', 'num_cni', 'addresse', 'num_telephone',
            'account_type', 'account_type_display', 'domaine', 'nom_organization',
            'is_active', 'date_joined', 'last_login', 'full_name'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'account_type_display',
            'genre_display', 'full_name'
        ]
        extra_kwargs = {
            'num_telephone': {'validators': []},  # Désactive la validation par défaut pour permettre la mise à jour
            'num_cni': {'validators': []},
            'id_cadastrale': {'validators': []}
        }

    def get_full_name(self, obj):
        return f"{obj.prenom} {obj.nom}" if obj.prenom and obj.nom else obj.username

    def validate_email(self, value):
        """Validation personnalisée de l'email"""
        if self.instance and User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Format d'email invalide.")
        return value

    def validate_num_telephone(self, value):
        """Validation du numéro de téléphone"""
        if not value.startswith('6') or len(value) != 9 or not value.isdigit():
            raise serializers.ValidationError("Le numéro doit commencer par 6 et contenir 9 chiffres.")
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'genre', 'date_naissance',
            'id_cadastrale', 'num_cni', 'addresse', 'num_telephone',
            'account_type', 'domaine', 'nom_organization', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'num_telephone': {'validators': []}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'genre', 'date_naissance',
            'addresse', 'num_telephone', 'domaine', 'nom_organization'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False}
        }

    def update(self, instance, validated_data):
        # Permet la mise à jour partielle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance