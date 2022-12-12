from rest_framework import serializers
from restaurantFood.models.food import RestaurantFood
from food.models.type import FoodType
from food.models.category import FoodCategory
from food.models.food_picture import FoodImage
from restaurantFood.models.ingredient import Ingredient


class RestaurantFoodSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    foodType = serializers.PrimaryKeyRelatedField(
        queryset=FoodType.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    foodCategory = serializers.PrimaryKeyRelatedField(
        queryset=FoodCategory.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=True,
        allow_empty=True,
        many=True
    )

    foodPicture = serializers.ImageField(allow_null=True, required=False)
    foodPicture_related = serializers.PrimaryKeyRelatedField(
        queryset=FoodImage.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        """Docstring for class."""

        model = RestaurantFood
        fields = ['id', 'name', 'reference', 'description', 'is_active',
                  'foodType', 'foodCategory', 'foodPicture', 'foodPicture_related', 'created_by',
                  'ingredients', 'price', 'nutritional_value', 'cooking_time']
        read_only_fields = ['reference', 'is_active', 'created_by']


class ViewRestaurantFoodSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    foodType = serializers.PrimaryKeyRelatedField(
        queryset=FoodType.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    foodCategory = serializers.PrimaryKeyRelatedField(
        queryset=FoodCategory.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    ingredients = serializers.ListField(child=serializers.CharField())

    foodPicture = serializers.ImageField(allow_null=True, required=False)
    foodPicture_related = serializers.PrimaryKeyRelatedField(
        queryset=FoodImage.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        """Docstring for class."""

        model = RestaurantFood
        fields = ['id', 'name', 'reference', 'description', 'is_active',
                  'foodType', 'foodCategory', 'foodPicture', 'foodPicture_related', 'created_by',
                  'ingredients', 'price', 'nutritional_value', 'cooking_time']
        read_only_fields = ['reference', 'is_active', 'created_by']

