import logging
import Levenshtein
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from core.tenant import set_tenant
from food.models.food_picture import FoodPicture
from food.serializers.food_picture import FoodPictureSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

logger = logging.getLogger("myLogger")


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_food_picture_from_name(request):
    """Docstring for function."""
    user = request.user
    if user.has_perm('restaurantFood.view_restaurantfood') is False:
        logger.warning(
            "Vous n'avez pas accès à la liste des photos des plats",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la liste des photos des plats"},
            status=status.HTTP_403_FORBIDDEN)
    set_tenant(request)
    queryset = FoodPicture.objects.filter(is_active=True, is_deleted=False)
    name = request.query_params.get('name', None)
    if name is None:
        logger.info(
            "Vous devez renseigner un nom de plat",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {"message": "Vous devez renseigner un nom de plat"},
            status.HTTP_400_BAD_REQUEST)
    name = str(name).strip()
    pic = None
    for picture in queryset:
        x = picture.name.strip()
        if Levenshtein.distance(name, x) <= 3:
            pic = picture
            break
    if pic is not None:
        serializer = FoodPictureSerializer(pic).data
    else:
        serializer = {
            "message": "Nom non compatible"
        }

    logger.info(
        "Les photos des plats renvoyés avec succes",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        serializer,
        status.HTTP_200_OK)

