from rest_framework import serializers
from restaurantDrink.models.drink import RestaurantDrink
from drink.models.type import DrinkType
from drink.models.category import DrinkCategory
from drink.models.drink import Drink


class RestaurantDrinkSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    drinkType = serializers.PrimaryKeyRelatedField(
        queryset=DrinkType.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=False,
        allow_null=True,
        allow_empty=True
    )
    drinkCategory = serializers.PrimaryKeyRelatedField(
        queryset=DrinkCategory.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=False,
        allow_null=True,
        allow_empty=True
    )
    admin_drink = serializers.PrimaryKeyRelatedField(
        queryset=Drink.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=False,
        allow_null=True,
        allow_empty=True
    )

    class Meta:
        """Docstring for class."""

        model = RestaurantDrink
        fields = ['id', 'name', 'reference', 'description', 'is_active',
                  'drinkType', 'drinkCategory', 'drinkPicture', 'created_by',
                  'price', 'admin_drink']
        read_only_fields = ['reference', 'is_active', 'created_by']
