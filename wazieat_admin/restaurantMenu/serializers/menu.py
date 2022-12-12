from rest_framework import serializers
from restaurantMenu.models.menu import Menu
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from restaurantMenu.models.publicationPeriod import PublicationPeriod


class MenuSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    foods = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantFood.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False,
        many=True
    )
    drinks = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantDrink.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False,
        many=True
    )

    period = serializers.PrimaryKeyRelatedField(
        queryset=PublicationPeriod.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )

    real_price = serializers.FloatField(required=False)

    class Meta:
        """Docstring for class."""

        model = Menu
        fields = ['id', 'name', 'reference', 'description', 'is_active',
                  'foods', 'calculated_price', 'real_price', 'drinks',
                  'status_price', 'percent', 'period', 'created_by']
        read_only_fields = ['reference', 'is_active', 'created_by', 'calculated_price', 'real_price']
