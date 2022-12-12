from rest_framework import serializers
from drink.models.category import DrinkCategory
from drink.models.drink import Drink


class DrinkSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    drinkCategory = serializers.PrimaryKeyRelatedField(
        queryset=DrinkCategory.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )

    drinkPicture = serializers.ImageField()

    class Meta:
        """Docstring for class."""

        model = Drink
        fields = ['id', 'name', 'reference', 'description', 'is_active',
                  'drinkCategory', 'drinkPicture', 'created_by']
        read_only_fields = ['reference', 'is_active', 'created_by']

