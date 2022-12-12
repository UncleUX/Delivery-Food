import logging
from datetime import datetime, timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantFood.models.food import RestaurantFood
from restaurantFood.serializers.food import RestaurantFoodSerializer
from core.schemas.schema_restaurant_food import schema_response_food_list
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Liste des plats ayant au moins le même plat',
    schema=schema_response_food_list,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='get',
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def same_price_food(request, food):
    """Docstring for function."""
    user = request.user
    if user.has_perm('restaurantFood.view_restaurantfood') is False:
        logger.warning(
            "Vous n'avez pas accès à la liste des plats",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la liste des plats"},
            status=status.HTTP_403_FORBIDDEN)
    set_tenant(request)
    try:
        food = RestaurantFood.objects.get(pk=food, is_active=True, is_deleted=False)
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
    price = food.price
    foods = RestaurantFood.objects.all().filter(price__gte=price, is_active=True, is_deleted=False)
    foods = list(foods)
    foods.remove(food)
    serializer = RestaurantFoodSerializer(foods, many=True)
    logger.info(
        "Liste des plats ayant au moins le même plat",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        serializer.data,
        status.HTTP_200_OK)



