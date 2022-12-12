from django.urls import path
from .views.same_price_food import same_price_food
from .views.get_food_picture_from_name import get_food_picture_from_name


urlpatterns = [
    path('food/same/price/<int:food>', same_price_food, name='same_price_food'),
    path('food/picture', get_food_picture_from_name, name='get_food_picture_from_name'),
]
