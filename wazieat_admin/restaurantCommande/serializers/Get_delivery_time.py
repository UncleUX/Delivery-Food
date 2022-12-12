from rest_framework import serializers
from accounts.models.restaurant import Restaurant
from restaurantDrink.models.drink import RestaurantDrink


class GetDeliveryTimeSerializer(serializers.Serializer):
    """Docstring for class."""

    origins = serializers.CharField(
        required=True, allow_null=False, allow_blank=False
    )
    destinations = serializers.CharField(
        required=True, allow_null=False, allow_blank=False
    )


class SourceSerializer(serializers.Serializer):
    """Docstring for class."""

    commande = serializers.IntegerField(required=True, allow_null=False)
    restaurant = serializers.IntegerField(required=True, allow_null=False)


class GetOneDeliveryTimeSerializer(serializers.Serializer):
    """Docstring for class."""

    origin = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    source = serializers.ListField(required=True, allow_null=False, child=SourceSerializer())
