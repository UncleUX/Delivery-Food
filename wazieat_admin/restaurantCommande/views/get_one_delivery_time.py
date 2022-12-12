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
from restaurantCommande.serializers.Get_delivery_time import GetOneDeliveryTimeSerializer
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


@swagger_auto_schema(method='post',
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_one_delivery_time(request):
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
    serializer = GetOneDeliveryTimeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    for data in serializer.validated_data['source']:
        print('data => ', data)
        try:
            restaurant = Restaurant.objects.get(pk=data['restaurant'], is_active=True)
        except Restaurant.DoesNotExist:
            logger.warning(
                "Le restaurant d'identifiant " + str(data['restaurant']) + " n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Le restaurant d'identifiant " + str(data['restaurant']) + " n'existe pas"},
                status=status.HTTP_400_BAD_REQUEST)
        set_tenant_from_restaurant(restaurant)
        try:
            commande = Commande.objects.get(pk=data['commande'], is_active=True)
        except Commande.DoesNotExist:
            logger.warning(
                "La commande d'identifiant " + str(data['commande']) + " du restaurant d'identifiant " + str(data['restaurant']) + " n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "La commande d'identifiant " + str(data['commande']) + " du restaurant d'identifiant " + str(data['restaurant']) + " n'existe pas"},
                status=status.HTTP_400_BAD_REQUEST)
    results = []
    for data in serializer.validated_data['source']:
        restaurant = Restaurant.objects.get(pk=data['restaurant'], is_active=True)
        set_tenant_from_restaurant(restaurant)
        commande = Commande.objects.get(pk=data['commande'], is_active=True)
        location = str(restaurant.location[0]) + ', ' + str(restaurant.location[1])
        origin = str(serializer.validated_data['origin']) + '|' + location
        destination = location + '|' + str(commande.delivery_location[0]) + ', ' + str(commande.delivery_location[1])
        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="
        url = url + origin + "&destinations="
        url = url + destination
        url = url + "&key=" + str(settings.MAP_API_KEY)
        result = {}
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

        rows = response.json()['rows']
        result['origin-restaurant'] = rows[0]['elements'][0]
        result['restaurant-destination'] = rows[1]['elements'][1]
        results.append(result)

    logger.info(
        "Durée des trajets renvoyée avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        results,
        status.HTTP_200_OK)
