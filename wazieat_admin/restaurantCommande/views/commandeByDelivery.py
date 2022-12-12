import logging
from datetime import datetime, timezone
from uuid import uuid4
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from accounts.models.user import User
from django.db import connection
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantCommande.models.note import Note
from accounts.models.restaurant import Restaurant
from restaurantCommande.models.commande import Commande
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from core.schemas.schema_commande import schema_response_commande
from restaurantCommande.utils import *

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Liste des commandes d\'un livreur',
    schema=schema_response_commande,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='get',
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def commande_by_delivery(request):
    """Docstring for function."""
    user = request.user
    if user.delivery is None and user.is_super() is False:
        logger.error(
            {'message': "Vous n'avez pas les accès nécessaires."},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas les accès nécessaires."},
            status.HTTP_403_FORBIDDEN)
    connection.set_schema_to_public()
    deli = request.query_params.get('delivery', None)
    if deli is None and user.is_super() is True:
        logger.warning(
            "Livreur absent en paramètre",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Livreur absent en paramètre"},
            status=status.HTTP_400_BAD_REQUEST)
    delivery = None
    if user.is_super() is True:
        try:
            delivery = User.objects.get(pk=int(deli), is_active=True, is_deleted=False, delivery__isnull=False, is_client=False)
        except User.DoesNotExist:
            logger.warning(
                "Livreur inexistant",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Livreur inexistant"},
                status=status.HTTP_400_BAD_REQUEST)
    if user.delivery is not None:
        delivery = request.user
    commandes = []
    # Gestion des tenants en fonction des utilisateurs
    for restaurant in Restaurant.objects.all().filter(is_active=True):
        set_tenant_from_restaurant(restaurant)
        instances = []
        try:
            instances = Commande.objects.all().filter(delivery_validated_by=delivery, is_active=True, is_deleted=False)
        except Commande.DoesNotExist:
            pass
        for instance in instances:
            note = Note.objects.all().filter(commande=instance).order_by('-id')
            result = get_commande(instance, note, restaurant)
            # Same price
            result['food_same_price'] = get_food_same_price(instance)
            result['drink_same_price'] = get_drink_same_price(instance)
            commandes.append(result)

    logger.info(
        "Liste des commandes du livreur renvoyé avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        commandes,
        status.HTTP_200_OK)

