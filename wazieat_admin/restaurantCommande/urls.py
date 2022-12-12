from django.urls import path
from .views.note import list_note, change_note, create_note
from .views.restaurant_validate_commande import restaurant_validate_commande
from .views.delivery_validate_commande import delivery_validate_commande
from .views.delivery_check_commande import delivery_check_commande
from .views.livraison_commande import livraison_commande
from .views.commandeByDelivery import commande_by_delivery
from .views.list_all_command import list_all_command
from .views.list_all_validated_command import list_all_validated_command
from .views.list_all_delivered_command import list_all_delivered_command
from .views.list_all_check_command import list_all_check_command
from .views.Get_delivery_time import get_delivery_time
from .views.note_service import create_note_service, change_note_service
from .views.get_one_delivery_time import get_one_delivery_time
from .views.suggestion_request_commande import suggestion_request_commande
from .views.suggestion_response_commande import suggestion_response_commande


urlpatterns = [
    path('note/commande/<int:commande>', list_note, name='list_note'),
    path('note/<int:note>/commande', change_note, name='change_note'),
    path('note/commande', create_note, name='create_note'),
    path('restaurant/validation/commande/<int:commande>', restaurant_validate_commande, name='restaurant_validate_commande'),
    path('delivery/validation/commande/<int:commande>', delivery_validate_commande, name='delivery_validate_commande'),
    path('delivery/check/commande/<int:commande>', delivery_check_commande, name='delivery_check_commande'),
    path('delivery/livraison/commande/<int:commande>', livraison_commande, name='livraison_commande'),
    path('delivery/commande', commande_by_delivery, name='commande_by_delivery'),
    path('command', list_all_command, name='list_all_command'),
    path('restaurant/suggestion/commande', suggestion_request_commande, name='suggestion_request_commande'),
    path('restaurant/suggestion/response/commande', suggestion_response_commande, name='suggestion_response_commande'),
    path('validate/command', list_all_validated_command, name='list_all_validated_command'),
    path('restaurant/delivered/command', list_all_delivered_command, name='list_all_delivered_command'),
    path('restaurant/checked/command', list_all_check_command, name='list_all_check_command'),
    path('delivery/duration', get_delivery_time, name='get_delivery_time'),
    path('client/note', create_note_service, name='create_note_service'),
    path('client/change/note/<int:note>', change_note_service, name='change_note_service'),
    path('delivery/duration/restaurant', get_one_delivery_time, name='get_one_delivery_time'),
]
