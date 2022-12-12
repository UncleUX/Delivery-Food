from rest_framework import serializers
from drink.models.type import DrinkType


class DrinkTypeSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    class Meta:
        """Docstring for class."""

        model = DrinkType
        fields = ['id', 'name', 'reference', 'description', 'is_active']
        read_only_fields = ['reference', 'is_active']
