from rest_framework import serializers
from .models import User, Contributor


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','password', 'username', 'age', 'can_be_contacted', 'can_data_be_shared', 'first_name',
                  'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}  # Empêche le mot de passe d'être affiché
        }

    def create(self, validated_data):
        # Hacher le mot de passe avant de créer l'utilisateur
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hachage du mot de passe
        user.save()
        return user


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project']
        read_only_fields = ['id', 'project']
