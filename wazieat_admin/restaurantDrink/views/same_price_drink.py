import logging
from datetime import datetime, timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantDrink.models.drink import RestaurantDrink
from restaurantDrink.serializers.drink import RestaurantDrinkSerializer
from core.schemas.schema_restaurant_drink import schema_response_drink_list
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Liste des boissons ayant au moins le même plat',
    schema=schema_response_drink_list,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='get',
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def same_price_drink(request, drink):
    """Docstring for function."""
    user = request.user
    if user.has_perm('restaurantDrink.view_restaurantdrink') is False:
        logger.warning(
            "Vous n'avez pas accès à la liste des boissons",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la liste des boissons"},
            status=status.HTTP_403_FORBIDDEN)
    set_tenant(request)
    try:
        drink = RestaurantDrink.objects.get(pk=drink, is_active=True, is_deleted=False)
    except RestaurantDrink.DoesNotExist:
        logger.warning(
            "Une boisson avec cette clé primaire n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Une boisson avec cette clé primaire n'existe pas"},
            status=status.HTTP_400_BAD_REQUEST)
    price = drink.price
    drinks = RestaurantDrink.objects.all().filter(price__gte=price, is_active=True, is_deleted=False)
    drinks = list(drinks)
    drinks.remove(drink)
    serializer = RestaurantDrinkSerializer(drinks, many=True)
    logger.info(
        "Liste des boissons ayant au moins le même plat",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        serializer.data,
        status.HTTP_200_OK)



