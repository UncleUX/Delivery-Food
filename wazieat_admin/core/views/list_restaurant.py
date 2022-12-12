import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.db import connection
from geopy import distance
from accounts.models.restaurant import Restaurant
from accounts.serializers.restaurant import RestaurantSerializer
from core.pagination import CustomPageNumberPagination
from core.schemas.schema_restaurant import schema_response_restaurant_list
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


logger = logging.getLogger("myLogger")

radius_param = openapi.Parameter('radius', openapi.IN_QUERY, description="Rayon", type=openapi.TYPE_INTEGER, required=True)
long_param = openapi.Parameter('long', openapi.IN_QUERY, description="Longitude de la position centrale", type=openapi.TYPE_NUMBER, required=True)
lat_param = openapi.Parameter('lat', openapi.IN_QUERY, description="Latitude de la position centrale", type=openapi.TYPE_NUMBER, required=True)
page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER)
size_param = openapi.Parameter('size', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER)

correct_response = openapi.Response(
    description='',
    schema=schema_response_restaurant_list,)
bad_request = openapi.Response('Message de mauvaise requête')
forbidden_request = openapi.Response('Pas de permissions')
error_response = openapi.Response('Message d\'erreur')


@swagger_auto_schema(method='get',
                     manual_parameters=[radius_param, long_param, lat_param, page_param, size_param],
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response, 412: error_response})
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def list_restaurant(request):
    """Docstring for function."""
    user = request.user
    if user.is_super() is False:
        logger.error(
            {'message': "seul le super admin peut visualiser les restaurants autour d'une position"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "seul le super admin peut visualiser les restaurants autour d'une position"},
            status.HTTP_403_FORBIDDEN)
    connection.set_schema_to_public()

    radius = request.query_params.get('radius', None)
    long = request.query_params.get('long', None)
    lat = request.query_params.get('lat', None)

    if radius is None or long is None or lat is None:
        logger.error(
            {'message': "Vous devez renseigner un long, un lat et un rayon"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous devez renseigner un long, un lat et un rayon"},
            status.HTTP_400_BAD_REQUEST)

    try:
        radius = float(radius)
        lat = float(lat)
        long = float(long)
    except Exception:
        logger.error(
            {'message': "Au moins une des valeurs fournies n'est pas un réel"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Au moins une des valeurs fournies n'est pas un réel"},
            status.HTTP_400_BAD_REQUEST)

    center_point = [{'lat': lat, 'lng': long}]
    radius = radius/1000  # in kilometer

    restaurants = []

    for res in Restaurant.objects.all().filter(location__isnull=False, is_active=True):
        location = res.location
        test_point = [{'lat': location[0], 'lng': location[1]}]
        center_point_tuple = tuple(center_point[0].values())  # (-7.7940023, 110.3656535)
        test_point_tuple = tuple(test_point[0].values())  # (-7.79457, 110.36563)

        dis = distance.distance(center_point_tuple, test_point_tuple).km
        print("Distance: {}".format(dis))  # Distance: 0.0628380925748918

        if dis <= radius:
            restaurants.append(res)

    # Pagination
    obj_pagine = CustomPageNumberPagination()
    page = obj_pagine.paginate_queryset(restaurants, request)
    res = None
    if page is not None:
        serializer = RestaurantSerializer(page, many=True)
        res = obj_pagine.get_paginated_response(serializer.data)
    else:
        serializer = RestaurantSerializer(restaurants, many=True)

    result = serializer.data

    # donnees liees a la pagination
    if res is not None:
        resultat = {
            'count': res.data['count'],
            'next': res.data['next'],
            'previous': res.data['previous'],
            'results': result
        }
    else:
        resultat = result

    logger.info(
        "Liste des restaurants autour de nous renvoyés avec succes",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(resultat, status.HTTP_200_OK)
