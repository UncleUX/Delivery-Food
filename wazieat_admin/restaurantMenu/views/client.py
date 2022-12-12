import logging
import datetime
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from accounts.models.restaurant import Restaurant
from restaurantMenu.models.menu import Menu
from restaurantMenu.serializers.publicationPeriod import PublicationPeriodSerializer
from restaurantMenu.models.publicationPeriod import PublicationPeriod
from accounts.serializers.user import UserSerializer
from restaurantFood.serializers.food import RestaurantFoodSerializer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


logger = logging.getLogger("myLogger")

schema_response = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(title="id", description="Identifiant du menu", type=openapi.TYPE_INTEGER,),
            "reference": openapi.Schema(title="reference", description="Reference du menu", type=openapi.TYPE_STRING,),
            "name": openapi.Schema(title="name", description="Nom du menu", type=openapi.TYPE_STRING,),
            "description": openapi.Schema(title="description", description="Description du menu", type=openapi.TYPE_STRING,),
            "is_active": openapi.Schema(title="is_active", description="Status d'activation du menu", type=openapi.TYPE_BOOLEAN,),
            "calculated_price": openapi.Schema(title="calculated_price", description="Prix calculé du menu", type=openapi.TYPE_NUMBER,),
            "real_price": openapi.Schema(title="real_price", description="Prix réel du menu", type=openapi.TYPE_NUMBER,),
            "status_price": openapi.Schema(title="status_price", description="Prix à considérer", type=openapi.TYPE_INTEGER,),
            "foods": openapi.Schema(
                title="foods", description="Plats du menu", type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(title="id", description="Identifiant du plat", type=openapi.TYPE_INTEGER,),
                        "reference": openapi.Schema(title="reference", description="Reference du plat", type=openapi.TYPE_STRING,),
                        "name": openapi.Schema(title="name", description="Nom du plat", type=openapi.TYPE_STRING,),
                        "description": openapi.Schema(title="description", description="Description du plat", type=openapi.TYPE_STRING,),
                        "is_active": openapi.Schema(title="", description="Status d'activation du menu", type=openapi.TYPE_BOOLEAN,),
                        "foodType": openapi.Schema(title="foodType", description="Identifiant du type de plat", type=openapi.TYPE_INTEGER,),
                        "foodCategory": openapi.Schema(title="foodCategory", description="Identifiant de la catégorie de plat", type=openapi.TYPE_INTEGER,),
                        "foodPicture": openapi.Schema(title="foodPicture", description="Chemin de l'image du plat", type=openapi.TYPE_STRING,),
                        "origin": openapi.Schema(title="origin", description="Origine du plat", type=openapi.TYPE_STRING,),
                        "price": openapi.Schema(title="price", description="Prix du plat", type=openapi.TYPE_INTEGER,),
                        "ingredients": openapi.Schema(title="ingredients", description="Identifiants des ingredients du plat", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                        "created_by": openapi.Schema(title="created_by", description="Identifiant de l'utilisateur qui a créé le plat", type=openapi.TYPE_INTEGER,),
                    },
                ),
            ),
            "created_by": openapi.Schema(title="created_by", description="Identifiant de l'utilisateur qui créé le menu", type=openapi.TYPE_INTEGER,),
            "period": openapi.Schema(title="period", description="Période de publication du menu", type=openapi.TYPE_INTEGER,),
        }
    )
)

page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER)
size_param = openapi.Parameter('size', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER)

correct_response = openapi.Response(
    description='Liste des menus du restaurant',
    schema=schema_response,)
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


@swagger_auto_schema(method='get',
                     manual_parameters=[page_param, size_param],
                     responses={200: correct_response, 400: bad_request, 412: error_response})
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def list_menu(request, restaurant):
    """Docstring for function."""
    user = request.user
    restau = Restaurant.objects.get(pk=restaurant, is_active=True)
    set_tenant_from_restaurant(restau)
    menus = Menu.objects.all()
    results = []
    for men in menus:
        if men.period is not None:
            period = men.period
            today = datetime.date.today()
            if period.end_date is not None and today <= period.end_date:
                if today >= period.start_date:
                    res = {
                        'id': men.id,
                        'reference': men.reference,
                        'name': men.name,
                        'description': men.description,
                        'is_active': men.is_active,
                        'calculated_price': men.calculated_price,
                        'real_price': men.real_price,
                        'status_price': men.get_status_price_display(),
                        'percent': men.percent,
                        'foods': RestaurantFoodSerializer(men.foods.all(), many=True).data,
                        'created_by': UserSerializer(men.created_by).data,
                        'period': PublicationPeriodSerializer(period).data
                    }
                    results.append(res)

    size = request.query_params.get('size', None)
    page = request.query_params.get('page', None)
    if size is not None and page is not None:
        paginator = Paginator(results, size)
        try:
            results = paginator.page(page).object_list
        except PageNotAnInteger:
            results = paginator.page(1).object_list
        except EmptyPage:
            results = paginator.page(paginator.num_pages).object_list

    logger.error(
        "Liste des menus du restaurant renvoyé avec succes",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        results,
        status.HTTP_200_OK)

