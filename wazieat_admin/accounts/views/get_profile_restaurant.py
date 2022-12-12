import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models.user import User
from django.conf import settings
from django.db import connection
from accounts.models.restaurant import Restaurant
from accounts.serializers.restaurant import RestaurantSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.utils import *

logger = logging.getLogger("myLogger")


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_profile_restaurant(request, restaurant):
    """Docstring for function."""
    user = request.user
    connection.set_schema_to_public()
    try:
        restau = Restaurant.objects.get(pk=restaurant, is_active=True)
    except Restaurant.DoesNotExist:
        logger.warning(
            "Un restaurant avec cette clé primaire n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Un restaurant avec cette clé primaire n'existe pas"},
            status=status.HTTP_400_BAD_REQUEST)
    data = {}
    if restau is not None:
        serializer = RestaurantSerializer(restau)
        data = get_profile_restaurant_detail(restau, serializer.data)

    logger.info(
        "Profile du restaurant renvoyé avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        data=data,
        status=status.HTTP_200_OK)

