from rest_framework import serializers
from food.models.category import FoodCategory


class FoodCategorySerializer(serializers.ModelSerializer):
    """Docstring for class."""

    class Meta:
        """Docstring for class."""

        model = FoodCategory
        fields = ['id', 'name', 'reference', 'description', 'is_active']
        read_only_fields = ['reference', 'is_active']
