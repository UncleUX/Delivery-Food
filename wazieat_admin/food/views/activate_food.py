import logging
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from core.tenant import set_tenant_from_restaurant
from restaurantFood.models.food import RestaurantFood
from accounts.models.restaurant import Restaurant
from food.serializers.activate_food import ActivateFoodSerializer
from rest_framework.permissions import IsAuthenticated
from restaurantFood.serializers.food import RestaurantFoodSerializer
from rest_framework.decorators import api_view, permission_classes
from restaurantFood.utils import *


logger = logging.getLogger("myLogger")


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def activate_food(request, food):
    """Docstring for function."""
    user = request.user
    if user.is_super() is False:
        logger.warning(
            "Vous n'avez pas accès pour activer un plat d'un restaurant",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès pour activer un plat d'un restaurant"},
            status=status.HTTP_403_FORBIDDEN)
    serializer = ActivateFoodSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        restaurant = Restaurant.objects.get(pk=request.data['restaurant'], is_active=True)
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
    mes = None
    set_tenant_from_restaurant(restaurant)
    try:
        food = RestaurantFood.objects.get(pk=food, is_active=False, is_deleted=False)
    except RestaurantFood.DoesNotExist:
        logger.warning(
            "Un plat avec cette clé primaire n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Un plat avec cette clé primaire n'existe pas"},
            status=status.HTTP_400_BAD_REQUEST)

    if serializer.validated_data['valid_status'] is True:
        try:
            mes = serializer.validated_data['reason']
        except KeyError:
            pass
        food.is_active = True
    else:
        try:
            mes = serializer.validated_data['reason']
        except KeyError:
            logger.warning(
                "Vous devez mentionner la raison du rejet du plat",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous devez mentionner la raison du rejet du plat"},
                status=status.HTTP_400_BAD_REQUEST)
    food.activated_by = user
    food.activated_reason = mes
    food.save()
    value = RestaurantFoodSerializer(food).data
    data = get_food(food, value['foodPicture'])
    logger.info(
        "L'activation/désactivation du plat avec succes",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        data,
        status.HTTP_200_OK)

