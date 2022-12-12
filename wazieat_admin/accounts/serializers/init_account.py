from rest_framework import serializers
from .validate_password import *


class InitAccountSerializer(serializers.Serializer):
    """Docstring for class."""

    token = serializers.CharField(required=True)
    phone = serializers.CharField(max_length=100, required=True)


class LoginSerializer(serializers.Serializer):
    """Docstring for class."""

    phone = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=100, required=True)
