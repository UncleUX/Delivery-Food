from django.urls import path
from .views import *
from .views.update_delivery_location import ChangeDeliveryLocationView

urlpatterns = [
    path('map/restaurants', list_restaurant, name='list_restaurant'),
    path('delivery/change/location', ChangeDeliveryLocationView.as_view(), name='update_delivery_location'),
]
