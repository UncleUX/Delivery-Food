from rest_framework import serializers
from food.models.type import FoodType


class FoodTypeSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    class Meta:
        """Docstring for class."""

        model = FoodType
        fields = ['id', 'name', 'reference', 'description', 'is_active']
        read_only_fields = ['reference', 'is_active']
