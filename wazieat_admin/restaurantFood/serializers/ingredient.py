from rest_framework import serializers
from restaurantFood.models.ingredient import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    quantity = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        """Docstring for class."""

        model = Ingredient
        fields = ['id', 'name', 'reference', 'description', 'is_active',
                  'quantity', 'created_by']
        read_only_fields = ['reference', 'is_active', 'created_by']
