from accounts.models.user import User
from accounts.models.delivery import Delivery
from rest_framework import serializers
from .validate_password import *


class UserSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    pseudo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    picture = serializers.ImageField(required=True, allow_null=True)
    email = serializers.EmailField(required=True, allow_null=True, allow_blank=False)

    class Meta:
        """Docstring for class."""

        model = User
        fields = ['id', 'phone', 'email', 'picture', 'last_name', 'first_name',
                  'is_active', 'is_staff', 'is_admin', 'reference',
                  'roles', 'pseudo', 'is_client', 'delivery']
        read_only_fields = ['is_active', 'reference', 'is_client']


class UserPasswordSerializer(serializers.Serializer):
    """Docstring for class."""

    password = serializers.CharField(
        max_length=100,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(max_length=100)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    pseudo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField(required=True, allow_null=True, allow_blank=False)

    class Meta:
        """Docstring for class."""

        model = User
        fields = ['email', 'phone', 'picture', 'last_name', 'first_name', 'is_staff',
                  'is_admin', 'roles', 'pseudo', 'is_client']


class UserCreateSerializer(serializers.Serializer):
    """Docstring for class."""

    pseudo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.RegexField(required=True, regex=r'^\+?1?\d{9,15}$')
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=True)
    picture = serializers.ImageField(required=True, allow_null=True)
    last_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    is_staff = serializers.BooleanField(required=True)
    is_admin = serializers.BooleanField(required=True)

