from rest_framework import serializers
from restaurantMenu.models.menu import Menu
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from restaurantCommande.models.commande import Commande, MenuQuantity, FoodQuantity, DrinkQuantity
from drf_writable_nested import WritableNestedModelSerializer


class MenuQuantitySerializer(serializers.ModelSerializer):
    """Docstring for class."""
    menu = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )

    class Meta:
        """Docstring for class."""

        model = MenuQuantity
        fields = ['menu', 'quantity']


class FoodQuantitySerializer(serializers.ModelSerializer):
    """Docstring for class."""
    food = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantFood.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )

    class Meta:
        """Docstring for class."""

        model = FoodQuantity
        fields = ['food', 'quantity']


class DrinkQuantitySerializer(serializers.ModelSerializer):
    """Docstring for class."""
    drink = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantDrink.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )

    class Meta:
        """Docstring for class."""

        model = DrinkQuantity
        fields = ['drink', 'quantity']


class CommandeSerializer(WritableNestedModelSerializer):
    """Docstring for class."""

    food = FoodQuantitySerializer(source='foodquantity_set', many=True)
    drink = DrinkQuantitySerializer(source='drinkquantity_set', many=True)
    menu = MenuQuantitySerializer(source='menuquantity_set', many=True)

    class Meta:
        """Docstring for class."""

        model = Commande
        fields = ['id', 'reference', 'is_active',
                  'food', 'drink', 'menu', 'created_by', 'total_price',
                  'is_restaurant_valid', 'is_delivery_valid', 'created_at',
                  'updated_at', 'created_by', 'restaurant_validate_date',
                  'delivery_validate_date', 'restaurant_validated_by', 'delivery_validated_by',
                  'restaurant_cancel_validated_by', 'delivery_cancel_validated_by',
                  'delivery_location', 'token', 'is_restaurant_valid', 'is_delivery_valid',
                  'restaurant_cancel_date', 'delivery_cancel_date', 'delivery_check_date',
                  'is_delivery_check', 'status', 'delivery_date', 'cooking_time', 'site_delivery']
        read_only_fields = ['reference', 'is_active', 'created_by', 'total_price',
                            'is_valid', 'created_at', 'updated_at', 'created_by',
                            'restaurant_validate_date', 'delivery_validate_date',
                            'restaurant_validated_by', 'delivery_validated_by',
                            'restaurant_cancel_validated_by', 'delivery_cancel_validated_by',
                            'token', 'is_restaurant_valid', 'is_delivery_valid',
                            'restaurant_cancel_date', 'delivery_cancel_date', 'delivery_check_date',
                            'is_delivery_check', 'status', 'delivery_date', 'cooking_time']


class CommandeCreateSerializer(serializers.Serializer):
    """Docstring for class."""

    food = FoodQuantitySerializer(many=True)
    drink = DrinkQuantitySerializer(many=True)
    menu = MenuQuantitySerializer(many=True)
    note = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    restaurant = serializers.IntegerField(required=True)
    delivery_location = serializers.ListField(child=serializers.FloatField(), required=True)
    site_delivery = serializers.CharField(required=True)


