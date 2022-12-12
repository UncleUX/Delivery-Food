from django.urls import path
from .views.same_price_drink import same_price_drink


urlpatterns = [
    path('drink/same/price/<int:drink>', same_price_drink, name='same_price_drink'),
]
