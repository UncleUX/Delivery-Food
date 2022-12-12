from rest_framework import serializers
from drink.models.category import DrinkCategory


class DrinkCategorySerializer(serializers.ModelSerializer):
    """Docstring for class."""

    class Meta:
        """Docstring for class."""

        model = DrinkCategory
        fields = ['id', 'name', 'reference', 'description', 'is_active']
        read_only_fields = ['reference', 'is_active']
