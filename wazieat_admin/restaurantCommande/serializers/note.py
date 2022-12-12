from rest_framework import serializers
from restaurantCommande.models.commande import Commande
from accounts.models.user import User
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from restaurantCommande.models.note import NoteComments, NoteFood, NoteDrink, Note
from drf_writable_nested import WritableNestedModelSerializer


class NoteDrinkSerializer(serializers.ModelSerializer):
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

        model = NoteFood
        fields = ['id', 'comment', 'drink']


class NoteFoodSerializer(serializers.ModelSerializer):
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

        model = NoteFood
        fields = ['id', 'comment', 'food']


class NoteCommentsSerializer(WritableNestedModelSerializer):
    """Docstring for class."""

    foods = NoteFoodSerializer(many=True)
    drinks = NoteDrinkSerializer(many=True)

    class Meta:
        """Docstring for class."""

        model = NoteComments
        fields = ['id', 'comment', 'foods', 'drinks']


class NoteSerializer(WritableNestedModelSerializer):
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
    comments = NoteCommentsSerializer()

    def create(self, validated_data):
        com = NoteComments()
        com.comment = validated_data['comments']['comment']
        com.save()
        for f in validated_data['comments']['foods']:
            val = NoteFood()
            val.comment = f['comment']
            val.food = f['food']
            val.save()
            com.foods.add(val)
        for f in validated_data['comments']['drinks']:
            val = NoteDrink()
            val.comment = f['comment']
            val.drink = f['drink']
            val.save()
            com.drinks.add(val)
        note = Note()
        note.comments = com
        note.commande = validated_data['commande']
        note.created_by = validated_data['created_by']
        note.save()
        return note

    def update(self, instance, validated_data):
        instance.comments.delete()
        com = NoteComments()
        com.comment = validated_data['comments']['comment']
        com.save()
        for f in validated_data['comments']['foods']:
            val = NoteFood()
            val.comment = f['comment']
            val.food = f['food']
            val.save()
            com.foods.add(val)
        for f in validated_data['comments']['drinks']:
            val = NoteDrink()
            val.comment = f['comment']
            val.drink = f['drink']
            val.save()
            com.drinks.add(val)
        instance.comments = com
        instance.commande = validated_data['commande']
        instance.save()
        return instance

    class Meta:
        """Docstring for class."""

        model = Note
        fields = ['id', 'comments', 'reference', 'commande',
                  'created_by', 'created_at', 'updated_at']
        read_only_fields = ['reference', 'created_by', 'created_at', 'updated_at']



class NoteCreateSerializer(serializers.Serializer):
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
    comments = NoteCommentsSerializer()
    restaurant = serializers.IntegerField(required=True)
