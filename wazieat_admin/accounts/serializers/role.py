from rest_framework import serializers
from accounts.models.role import Role
from accounts.models.user import User
from django.contrib.auth.models import Permission


class RoleSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        """Docstring for class."""

        model = Role
        fields = ['id', 'name', 'permissions', 'is_active',
                  'reference', 'description']
        read_only_fields = ['is_active', 'reference']


class RoleCreateSerializer(serializers.Serializer):
    """Docstring for class."""

    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=True
    )
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=True
    )

