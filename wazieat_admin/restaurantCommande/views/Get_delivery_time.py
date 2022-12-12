import logging
import requests
import json
from datetime import datetime, timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantCommande.models.note import Note
from threading import Thread
from restaurantCommande.models.commande import Commande
from restaurantCommande.serializers.Get_delivery_time import GetDeliveryTimeSerializer
from accounts.models.restaurant import Restaurant
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "distance": openapi.Schema(title="distance", description="distance entre deux points", type=openapi.TYPE_STRING,),
        "duration": openapi.Schema(title="duration", description="durée du trajets pour cette distance", type=openapi.TYPE_STRING,),
    }
)

schema_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "origin-restaurant": schema,
        "restaurant-destination": schema
    }
)

correct_response = openapi.Response(
    description='Détermination de la durée de livraison de la commande par le livreur',
    schema=schema_response, )
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='get',
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_delivery_time(request):
    """Docstring for function."""
    user = request.user
    if user.delivery is None:
        logger.error(
            {'message': "Vous n'avez pas accès à cette fonctionnalité"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à cette fonctionnalité"},
            status.HTTP_403_FORBIDDEN)
    connection.set_schema_to_public()
    serializer = GetDeliveryTimeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="
    url = url + str(serializer.validated_data['origins']) + "&destinations="
    url = url + str(serializer.validated_data['destinations'])
    url = url + "&key=" + str(settings.MAP_API_KEY)

    response = requests.get(url)
    if response.status_code != 200:
        logger.info(
            "Erreur de configuration l'api de Google Maps",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            response.json(),
            status.HTTP_400_BAD_REQUEST)
    else:
        if 'error_message' in response.json():
            logger.info(
                "Erreur de l'api de Google Maps",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                response.json(),
                status.HTTP_400_BAD_REQUEST)

    logger.info(
        "Durée des trajets renvoyée avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        response.json(),
        status.HTTP_200_OK)
