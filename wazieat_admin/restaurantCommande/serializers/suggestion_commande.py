from rest_framework import serializers
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from restaurantCommande.models.commande import Commande


class FoodSuggestionCommandeSerializer(serializers.Serializer):
    """Docstring for class."""

    initial_food = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantFood.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    suggest_food = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantFood.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )


class DrinkSuggestionCommandeSerializer(serializers.Serializer):
    """Docstring for class."""

    initial_drink = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantDrink.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    suggest_drink = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantDrink.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )


class SuggestionCommandeSerializer(serializers.Serializer):
    """Docstring for class."""

    restaurant = serializers.IntegerField(required=True, allow_null=False)
    commande = serializers.PrimaryKeyRelatedField(
        queryset=Commande.objects.all().filter(
            is_active=True,
            is_deleted=False,
            status=1
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    foods = FoodSuggestionCommandeSerializer(many=True)
    drinks = DrinkSuggestionCommandeSerializer(many=True)


class SuggestionResponseCommandeSerializer(serializers.Serializer):
    """Docstring for class."""

    restaurant = serializers.IntegerField(required=True, allow_null=False)
    commande = serializers.PrimaryKeyRelatedField(
        queryset=Commande.objects.all().filter(
            is_active=True,
            is_deleted=False,
            status=1
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    response = serializers.BooleanField(required=True, allow_null=False)
