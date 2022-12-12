from food.serializers.food_picture import FoodImageSerializer
from food.serializers.type import FoodTypeSerializer
from accounts.serializers.user import UserSerializer
from restaurantFood.serializers.ingredient import IngredientSerializer
from food.serializers.category import FoodCategorySerializer


def get_food(food, picture=None):

    if picture is not None:
        foodPicture_related = None
    else:
        foodPicture_related = FoodImageSerializer(food.foodPicture_related).data

    data = {
        "id": food.id,
        "name": food.name,
        "reference": food.reference,
        "description": food.description,
        "is_active": food.is_active,
        "foodType": FoodTypeSerializer(food.foodType).data,
        "foodCategory": FoodCategorySerializer(food.foodCategory).data,
        "foodPicture": picture,
        "foodPicture_related": foodPicture_related,
        "created_by": UserSerializer(food.created_by).data,
        "price": food.price,
        "nutritional_value": food.nutritional_value,
        "cooking_time": food.cooking_time,
        "ingredients": IngredientSerializer(food.ingredients, many=True).data
    }
    return data
