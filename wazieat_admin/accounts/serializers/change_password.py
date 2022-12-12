from rest_framework import serializers
from .validate_password import *


class ChangePasswordSerializer(serializers.Serializer):
    """Docstring for class."""

    old_password = serializers.CharField(max_length=100)
    new_password = serializers.CharField(
        max_length=100,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(max_length=100)


class ResetPasswordSerializer(serializers.Serializer):
    """Docstring for class."""

    token = serializers.CharField(max_length=100)
    new_password = serializers.CharField(
        max_length=100,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(max_length=100)

