import json
import logging
from uuid import uuid4
import datetime
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.decorators import permission_classes
from django.conf import settings
from core.utils import send_mail
from django.db import connection
from accounts.models.module import Module
from drink.models.type import DrinkType
from drink.models.category import DrinkCategory
from food.models.category import FoodCategory
from food.models.type import FoodType
from notifications.notifications import notifications
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from accounts.serializers.restaurant import (RestaurantSerializer,
                                             RestaurantUpdateSerializer)
from accounts.serializers.user import UserSerializer
from accounts.models.restaurant import Restaurant, Domain, Picture
from accounts.models.user import User
from core.pagination import CustomPageNumberPagination
import requests
from accounts.utils import *

logger = logging.getLogger("myLogger")


class RestaurantViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    queryset = restaurants = Restaurant.objects.all().order_by('id')
    serializer_class = RestaurantSerializer
    parser_classes = [MultiPartParser]

    @permission_classes([IsAuthenticated])
    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.is_super() is False:
            logger.error(
                "Vous n'avez pas les droits nécessaires",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN
            )
        connection.set_schema_to_public()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        results = []
        for instance, ser in zip(queryset, serializer.data):
            data = get_restaurant(instance, ser)
            results.append(data)
        logger.info(
            "Liste des clients renvoyées avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(results)

    @permission_classes([IsAuthenticated])
    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        if request.user.is_super() is False:
            logger.warning(
                "Vous n'avez pas les droits nécessaires!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN
            )
        connection.set_schema_to_public()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = get_restaurant(instance, serializer.data)
        logger.info(
            "détail sur le restaurant renvoyé avec succès!",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response(data)

    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        if request.user.is_super() is False:
            logger.error(
                "Vous ne pouvez pas ajouter de wazieats.!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN
            )
        try:
            serializer_restaurant = RestaurantSerializer(data=request.data)
            serializer_user = UserSerializer(data=request.data)

            if serializer_restaurant.is_valid(raise_exception=True):
                # Données du formulaire
                if serializer_user.is_valid(raise_exception=True):
                    # pas de chiffre dans le nom de la société
                    name = serializer_restaurant.validated_data['name']
                    if name[0:3].isnumeric():
                        logger.warning(
                            "Les trois premiers caractères du nom d'un restaurant ne doit être un nombre",
                            extra={
                                'restaurant': request.user.restaurant,
                                'user': request.user.id
                            }
                        )
                        return Response({'message': "Les trois premiers caractères du nom d'un restaurant ne doit être un nombre"},
                                        status=status.HTTP_409_CONFLICT)

                    # Unicité du nom de société
                    num = Restaurant.objects.all().filter(
                        name=serializer_restaurant.validated_data['name']
                    ).count()
                    if num > 0:
                        logger.warning(
                            "Un restaurant avec ce nom existe dejà",
                            extra={
                                'restaurant': request.user.restaurant,
                                'user': request.user.id
                            }
                        )
                        return Response({'message': "Un restaurant avec ce nom existe dejà"},
                                        status=status.HTTP_409_CONFLICT)

                    # Génération du schema name
                    if Restaurant.objects.all().count() >= 1:
                        obj = Restaurant.objects.latest('id')
                        num = obj.id
                        schema = ''.join(e for e in serializer_restaurant.validated_data['name'] if e.isalnum()).lower()
                        schema = schema[0:3] + "_" + str(num)
                    else:
                        schema = ''.join(e for e in serializer_restaurant.validated_data['name'] if e.isalnum()).lower()
                        schema = schema[0:3] + "_0"

                    if len(serializer_restaurant.validated_data['picture_restaurant']) < 3:
                        logger.warning(
                            "Un restaurant doit avoir au moins 3 photos",
                            extra={
                                'restaurant': request.user.restaurant,
                                'user': request.user.id
                            }
                        )
                        return Response({'message': "Un restaurant doit avoir au moins 3 photos"},
                                        status=status.HTTP_409_CONFLICT)

                    serializer_restaurant = expand_field(serializer_restaurant, request)

                    # Création du restaurant
                    restaurant = serializer_restaurant.save(
                        schema_name=schema)

                    # create domain
                    domain = Domain()
                    domain.domain = schema
                    domain.tenant = restaurant
                    domain.is_primary = True
                    domain.save()

                    # Create a superAdmin
                    user = User.objects.create_admin(
                        phone=serializer_user.validated_data['phone'],
                        email=serializer_user.validated_data['email'],
                        restaurant=restaurant,     # restaurant_id
                        last_name=serializer_user.validated_data['last_name'],
                        first_name=serializer_user.validated_data['first_name'],
                    )
                    reset_token = uuid4()
                    user.reset_token = reset_token
                    user.password_requested_at = datetime.datetime.now()
                    user.save()
                    notifications(request, user)
                    data = get_restaurant(restaurant, serializer_restaurant.data)

                    logger.info(
                        "Schéma de restaurant créé avec succès.",
                        extra={
                            'restaurant': request.user.restaurant,
                            'user': request.user.id
                        }
                    )
                    return Response({'message': "OK"}, status.HTTP_201_CREATED)

                    # return Response(data, status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)

    @permission_classes([IsAuthenticated])
    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        if request.user.is_super() is False:
            logger.warning(
                "Vous n'avez pas les droits nécessaires",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN
            )
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = RestaurantUpdateSerializer(
            instance, data=request.data,
            partial=partial)
        if serializer.is_valid() is True:

            if len(serializer.validated_data['picture_restaurant']) < 3:
                logger.warning(
                    "Un restaurant doit avoir au moins 3 photos",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response({'message': "Un restaurant doit avoir au moins 3 photos"},
                                status=status.HTTP_409_CONFLICT)

            serializer = expand_field(serializer, request)

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            data = get_restaurant(instance, serializer.data)

            logger.info(
                "Restaurant modifié avec succès",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(data)
        else:
            logger.error(
                str(serializer.errors),
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(serializer.errors, status=status.HTTP_412_PRECONDITION_FAILED)

    @permission_classes([IsAuthenticated])
    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        if request.user.is_super() is False:
            logger.warning(
                "Vous n'avez pas les droits nécessaires",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        users = User.objects.filter(restaurant=instance)
        for user in users:
            username = str(uuid4())
            username = username + '@deleted.com'
            user.restaurant = None
            user.is_active = False
            user.is_deleted = True
            user.first_name = 'to_deleted'
            user.username = username
            user.save()

        # Delete authtoken
        for user in users:
            print(user.is_authenticated)
            if user.is_authenticated():
                user.auth_token.delete()

        restaurant.delete()
        for user in users:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM accounts_user WHERE id = %s", [user.id])

        logger.error(
            "Restaurant supprimé avec succès",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response(
            status=status.HTTP_204_NO_CONTENT)


def expand_field(serializer, request):

    datas = ["module", "drinkCategory", "drinkType", "foodType", "foodCategory"]
    for data in datas:
        if not serializer.validated_data[data]:
            modules = []
            for keys in request.data.keys():
                if str(keys).startswith(data):
                    s = None
                    if data == "module":
                        s = Module.objects.get(pk=int(request.data[str(keys)]), is_active=True, is_deleted=False)
                    elif data == "drinkCategory":
                        s = DrinkCategory.objects.get(pk=int(request.data[str(keys)]), is_active=True, is_deleted=False)
                    elif data == "drinkType":
                        s = DrinkType.objects.get(pk=int(request.data[str(keys)]), is_active=True, is_deleted=False)
                    elif data == "foodType":
                        s = FoodType.objects.get(pk=int(request.data[str(keys)]), is_active=True, is_deleted=False)
                    elif data == "foodCategory":
                        s = FoodCategory.objects.get(pk=int(request.data[str(keys)]), is_active=True, is_deleted=False)
                    if s is not None:
                        modules.append(s)
            serializer.validated_data[data] = modules

    return serializer
