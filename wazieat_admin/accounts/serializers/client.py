from accounts.models.user import User
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    pseudo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    picture = serializers.ImageField(required=True, allow_null=True)
    email = serializers.EmailField(required=True, allow_null=True, allow_blank=False)

    class Meta:
        """Docstring for class."""

        model = User
        fields = ['id', 'phone', 'picture', 'email', 'last_name', 'first_name',
                  'is_active', 'reference', 'pseudo', 'is_client']
        read_only_fields = ['is_active', 'reference', 'is_client']


class ClientUpdateSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    pseudo = serializers.CharField(required=False)
    picture = serializers.ImageField(required=True, allow_null=True)
    email = serializers.EmailField(required=True, allow_null=True, allow_blank=False)

    class Meta:
        """Docstring for class."""

        model = User
        fields = ['email', 'phone', 'picture', 'last_name', 'first_name', 'pseudo']


class ClientCreateSerializer(serializers.Serializer):
    """Docstring for class."""

    pseudo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.RegexField(required=True, regex=r'^\+?1?\d{9,15}$')
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=True)
    last_name = serializers.CharField(required=True)
    picture = serializers.ImageField(required=True, allow_null=True)
    first_name = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
