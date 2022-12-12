from rest_framework import serializers
from accounts.models.module import Module
from django.contrib.contenttypes.models import ContentType


class ModuleSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    contenttypes = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        many=True,
        allow_empty=False
    )

    class Meta:
        """Docstring for class."""

        model = Module
        fields = ['id', 'name', 'reference', 'description', 'contenttypes', 'is_active']
        read_only_fields = ['reference', 'is_active']
