from rest_framework import serializers
from .models import User, Contributor


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','password', 'username', 'age', 'can_be_contacted', 'can_data_be_shared', 'first_name',
                  'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined']


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = '__all__'