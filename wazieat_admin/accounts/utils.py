from accounts.serializers.module import ModuleSerializer
from drink.serializers.type import DrinkTypeSerializer
from drink.serializers.category import DrinkCategorySerializer
from food.serializers.type import FoodTypeSerializer
from food.serializers.category import FoodCategorySerializer


def get_restaurant(restaurant, ser):

    data = {
        "id": restaurant.id,
        "reference": restaurant.reference,
        "mane": restaurant.name,
        "email": restaurant.email,
        "phone": restaurant.phone,
        "social_network_link": restaurant.social_network_link,
        "internet_site": restaurant.internet_site,
        "restaurant_channel": restaurant.restaurant_channel,
        "opening_hour": restaurant.opening_hour,
        "closing_hour": restaurant.closing_hour,
        "immatriculation": restaurant.immatriculation,
        "location": restaurant.location,
        "created_at": restaurant.created_at,
        "updated_at": restaurant.updated_at,
        "rccm_document": ser['rccm_document'],
        "module": ModuleSerializer(restaurant.module, many=True).data,
        "drinkType": DrinkTypeSerializer(restaurant.drinkType, many=True).data,
        "drinkCategory": DrinkTypeSerializer(restaurant.drinkType, many=True).data,
        "foodCategory": DrinkTypeSerializer(restaurant.drinkType, many=True).data,
        "foodType": DrinkTypeSerializer(restaurant.drinkType, many=True).data,
        "profile_picture": ser['profile_picture'],
        "picture_restaurant": ser['picture_restaurant']
    }
    return data


def get_profile_restaurant_detail(restaurant, ser):
    data = {
        "id": restaurant.id,
        "reference": restaurant.reference,
        "mane": restaurant.name,
        "social_network_link": restaurant.social_network_link,
        "internet_site": restaurant.internet_site,
        "restaurant_channel": restaurant.restaurant_channel,
        "opening_hour": restaurant.opening_hour,
        "closing_hour": restaurant.closing_hour,
        "immatriculation": restaurant.immatriculation,
        "location": restaurant.location,
        "created_at": restaurant.created_at,
        "updated_at": restaurant.updated_at,
        "profile_picture": ser['profile_picture'],
        "picture_restaurant": ser['picture_restaurant']
    }
    return data

