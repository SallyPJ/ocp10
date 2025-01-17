from rest_framework import serializers
from .models import User, Contributor
from rest_framework.exceptions import ValidationError


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'username', 'age', 'can_be_contacted', 'can_data_be_shared', 'first_name',
                  'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'required': False},
            'is_superuser': {'required': False},
        }

    def create(self, validated_data):
        """
        Hash the password before creating the user.
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user

    def validate(self, attrs):
        """
        Custom validation to restrict access to sensitive fields (`is_staff` and `is_superuser`)
        to superusers only.
        """
        request = self.context.get('request')
        if request and not request.user.is_superuser:  # If the requesting user is not a superuser
            if 'is_staff' in attrs:
                raise ValidationError({"is_staff": "You are not allowed to set this field."})
            if 'is_superuser' in attrs:
                raise ValidationError({"is_superuser": "You are not allowed to set this field."})
        return attrs

    def update(self, instance, validated_data):
        """
        Prevent non-superusers from modifying sensitive fields (`is_staff` and `is_superuser`).
        """
        request = self.context.get('request')
        if request and not request.user.is_superuser:
            validated_data.pop('is_staff', None)  # Remove `is_staff` if present
            validated_data.pop('is_superuser', None)  # Remove `is_superuser` if present
        return super().update(instance, validated_data)


class ContributorSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'user_username', 'role', 'project', 'project_name']
        read_only_fields = ['id', 'project']
