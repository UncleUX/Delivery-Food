from rest_framework import serializers
from restaurantCommande.models.commande import Commande
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from drf_writable_nested import WritableNestedModelSerializer
from restaurantCommande.models.note_service import (NoteService, NoteRestaurantDrink,
                                                    NoteRestaurantFood, NoteDelivery,
                                                    NoteRestaurant)


class NoteRestaurantDrinkSerializer(serializers.ModelSerializer):
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
    note = serializers.IntegerField(required=True, min_value=0, max_value=5, allow_null=False)

    class Meta:
        """Docstring for class."""

        model = NoteRestaurantDrink
        fields = ['id', 'comment', 'drink', 'note']


class NoteRestaurantFoodSerializer(serializers.ModelSerializer):
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
    note = serializers.IntegerField(required=True, min_value=0, max_value=5, allow_null=False)

    class Meta:
        """Docstring for class."""

        model = NoteRestaurantFood
        fields = ['id', 'comment', 'food', 'note']


class NoteRestaurantSerializer(WritableNestedModelSerializer):
    """Docstring for class."""

    note = serializers.IntegerField(required=True, min_value=0, max_value=5, allow_null=False)
    foods = NoteRestaurantFoodSerializer(many=True)
    drinks = NoteRestaurantDrinkSerializer(many=True)

    class Meta:
        """Docstring for class."""

        model = NoteRestaurant
        fields = ['id', 'comment', 'foods', 'drinks', 'note']


class NoteDeliverySerializer(serializers.ModelSerializer):
    """Docstring for class."""

    note = serializers.IntegerField(required=True, min_value=0, max_value=5, allow_null=False)

    class Meta:
        """Docstring for class."""

        model = NoteDelivery
        fields = ['id', 'comment', 'note']


class NoteServiceSerializer(WritableNestedModelSerializer):
    """Docstring for class."""

    commande = serializers.PrimaryKeyRelatedField(
        queryset=Commande.objects.all().filter(
            is_active=True,
            is_deleted=False,
            status=5
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    note_delivery = NoteDeliverySerializer()
    note_restaurant = NoteRestaurantSerializer()

    def create(self, validated_data):
        deli = NoteDelivery()
        deli.comment = validated_data['note_delivery']['comment']
        deli.note = validated_data['note_delivery']['note']
        deli.save()
        res = NoteRestaurant()
        res.comment = validated_data['note_restaurant']['comment']
        res.note = validated_data['note_restaurant']['note']
        res.save()
        for f in validated_data['note_restaurant']['foods']:
            val = NoteRestaurantFood()
            val.comment = f['comment']
            val.note = f['note']
            val.food = f['food']
            val.save()
            res.foods.add(val)
        for f in validated_data['note_restaurant']['drinks']:
            val = NoteRestaurantDrink()
            val.comment = f['comment']
            val.note = f['note']
            val.drink = f['drink']
            val.save()
            res.drinks.add(val)
        note = NoteService()
        note.note_restaurant = res
        note.note_delivery = deli
        note.commande = validated_data['commande']
        note.created_by = validated_data['created_by']
        note.save()
        return note

    def update(self, instance, validated_data):
        instance.note_restaurant.delete()
        instance.note_delivery.delete()
        res = NoteRestaurant()
        res.comment = validated_data['note_restaurant']['comment']
        res.note = validated_data['note_restaurant']['note']
        res.save()
        deli = NoteDelivery()
        deli.comment = validated_data['note_delivery']['comment']
        deli.note = validated_data['note_delivery']['note']
        deli.save()
        for f in validated_data['note_restaurant']['foods']:
            val = NoteRestaurantFood()
            val.comment = f['comment']
            val.note = f['note']
            val.food = f['food']
            val.save()
            res.foods.add(val)
        for f in validated_data['note_restaurant']['drinks']:
            val = NoteRestaurantDrink()
            val.comment = f['comment']
            val.note = f['note']
            val.drink = f['drink']
            val.save()
            res.drinks.add(val)
        instance.note_restaurant = res
        instance.note_delivery = deli
        instance.commande = validated_data['commande']
        instance.save()
        return instance

    class Meta:
        """Docstring for class."""

        model = NoteService
        fields = ['id', 'note_delivery', 'reference', 'commande',
                  'created_by', 'created_at', 'updated_at', 'note_restaurant']
        read_only_fields = ['reference', 'created_by', 'created_at', 'updated_at']


class NoteServiceCreateSerializer(serializers.Serializer):
    """Docstring for class."""

    commande = serializers.PrimaryKeyRelatedField(
        queryset=Commande.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    note_livreur = serializers.IntegerField(required=True, min_value=0, max_value=5, allow_null=True)
    note_restaurant = serializers.IntegerField(required=True, min_value=0, max_value=5, allow_null=True)
    restaurant = serializers.IntegerField(required=True, allow_null=False)
    livreur = serializers.IntegerField(required=True, allow_null=False)
