from drink.serializers.type import DrinkTypeSerializer
from accounts.serializers.user import UserSerializer
from drink.serializers.category import DrinkCategorySerializer
from drink.serializers.drink import DrinkSerializer


def get_drink(drink, picture):

    data = {
        "id": drink.id,
        "name": drink.name,
        "reference": drink.reference,
        "description": drink.description,
        "is_active": drink.is_active,
        "drinkType": DrinkTypeSerializer(drink.drinkType).data,
        "drinkCategory": DrinkCategorySerializer(drink.drinkCategory).data,
        "admin_drink": DrinkSerializer(drink.admin_drink).data,
        "drinkPicture": picture,
        "created_by": UserSerializer(drink.created_by).data,
        "price": drink.price
    }
    return data
