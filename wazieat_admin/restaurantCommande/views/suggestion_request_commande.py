import json
import logging
from datetime import datetime, timezone
from uuid import uuid4
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from accounts.models.user import User
from django.db import connection
from threading import Thread
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from accounts.models.restaurant import Restaurant
from restaurantCommande.models.commande import Commande
from notifications.notif_cancel_commande import notif_cancel_suggest_commande
from restaurantCommande.serializers.suggestion_commande import SuggestionCommandeSerializer
from core.schemas.schema_commande import schema_response_commande
from restaurantCommande.utils import *

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Suggestion d\'une commande',
    schema=schema_response_commande,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='put',
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def suggestion_request_commande(request):
    """Docstring for function."""
    user = request.user
    if user.has_perm('restaurantCommande.change_commande') is False:
        logger.warning(
            "Vous n'avez pas accès à la suggestion des commandes",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la suggestion des commandes"},
            status=status.HTTP_403_FORBIDDEN)
    connection.set_schema_to_public()
    # Gestion des tenants en fonction des utilisateurs
    try:
        restaurant = Restaurant.objects.get(pk=request.data['restaurant'], is_active=True)
    except Restaurant.DoesNotExist:
        logger.warning(
            "Un restaurant avec cette cle primaire n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Un restaurant avec cette cle primaire n'existe pas"},
            status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        logger.warning(
            "Le champ restaurant est absent dans la requête",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Le champ restaurant est absent dans la requête"},
            status=status.HTTP_400_BAD_REQUEST)
    set_tenant_from_restaurant(restaurant)
    serializer = SuggestionCommandeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if check_foods_suggest(serializer) is False:
        logger.warning(
            "Un plat initial ne se trouve pas dans votre commande",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Un plat initial ne se trouve pas dans votre commande"},
            status=status.HTTP_400_BAD_REQUEST)
    if check_drinks_suggest(serializer) is False:
        logger.warning(
            "Une boisson initiale ne se trouve pas dans votre commande",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Une boisson initiale ne se trouve pas dans votre commande"},
            status=status.HTTP_400_BAD_REQUEST)
    commande = serializer.validated_data['commande']
    dic = {'foods': [], 'drinks': []}
    for item in serializer.validated_data['foods']:
        val = {'initial_food': item['initial_food'].id, 'suggest_food': item['suggest_food'].id}
        dic['foods'].append(val)
    for item in serializer.validated_data['drinks']:
        val = {'initial_drink': item['initial_drink'].id, 'suggest_drink': item['suggest_drink'].id}
        dic['drinks'].append(val)
    commande.suggestion = dic
    commande.restaurant_suggest_by = user
    commande.save()
    # Notification Client si commande non validée
    t1 = Thread(
        target=notif_cancel_suggest_commande,
        args=(request, commande, restaurant)
    )
    t1.start()
    note = Note.objects.all().filter(commande=commande).order_by('-id')
    result = get_commande(commande, note, restaurant)
    # Same price
    result['food_same_price'] = get_food_same_price(commande)
    result['drink_same_price'] = get_drink_same_price(commande)
    logger.info(
        "Liste des commandes du livreur renvoyé avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        result,
        status.HTTP_200_OK)
