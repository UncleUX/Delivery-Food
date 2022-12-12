import logging
from uuid import uuid4
import datetime
import requests
import json
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth import get_user_model
from core.pagination import CustomPageNumberPagination
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from django.conf import settings
from core.utils import send_mail
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from core.schemas.schema_user import schema_response_user
from accounts.serializers.user import (
    UserSerializer, UserUpdateSerializer,
    UserPasswordSerializer, UserCreateSerializer)
from accounts.models.restaurant import Restaurant
from accounts.models.user import User
from notifications.notifications import notifications
from core.pagination import CustomPageNumberPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Client',
    schema=schema_response_user,)
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


class UserViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]
    queryset = User.objects.all().filter(
                is_deleted=False,
                is_client=False,
                delivery=None).order_by('last_name')
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if request.user.is_super() or request.user.is_staff:
            users = get_user_model().objects.all().filter(
                is_deleted=False,
                is_client=False,
                delivery=None,
                restaurant=request.user.restaurant
            ).order_by('last_name')
        else:
            logger.error(
                "Vous n'avez pas les droits nécessaires",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous n'avez pas les droits nécessaires"
                },
                status.HTTP_403_FORBIDDEN
            )
        connection.set_schema_to_public()
        queryset = self.filter_queryset(users)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Liste des clients renvoyées avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        if request.user.is_staff is False:
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
        try:
            instance = get_user_model().objects.get(
                pk=kwargs['pk'],
                is_deleted=False,
                is_client=False,
                delivery=None,
                restaurant=request.user.restaurant
            )
        except User.DoesNotExist:
            logger.error(
                "Utilisateur inexistant!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )

            return Response(
                {"message": "Utilisateur inexistant"},
                status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        logger.info(
            "détail sur le client renvoyé avec succès!",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserCreateSerializer,
                         responses={200: correct_response, 400: bad_request, 412: error_response})
    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        admin = False
        staff = False
        if request.user.is_super():
            restaurant = None
            try:
                if request.data['is_admin']:
                    admin = request.data['is_admin']
            except KeyError:
                logger.error(
                    "Vous devez renseigner le champ is_admin",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {"message": "Vous devez renseigner le champ is_admin"},
                    status.HTTP_403_FORBIDDEN
                )
        elif request.user.is_staff:
            restaurant = request.user.restaurant
            try:
                if request.data['is_staff']:
                    staff = request.data['is_staff']
            except KeyError:
                logger.error(
                    "Vous devez renseigner le champ is_staff",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {"message": "Vous devez renseigner le champ is_staff"},
                    status.HTTP_403_FORBIDDEN
                )
        else:
            logger.error(
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

        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = get_user_model().objects.create_user(
                    phone=serializer.validated_data['phone'],
                    email=serializer.validated_data['email'],
                    last_name=serializer.validated_data['last_name'],
                    first_name=serializer.validated_data['first_name'],
                    restaurant=restaurant
                )
                reset_token = uuid4()
                user.reset_token = reset_token
                user.picture = serializer.validated_data['picture']
                user.password_requested_at = datetime.datetime.now()
                user.is_staff = staff
                user.is_admin = admin
                user.save()
                try:
                    if serializer.validated_data['is_staff'] is not None and serializer.validated_data['is_admin'] is not None:

                        user.save()
                except KeyError:
                    pass

                notifications(request, user)

                logger.info(
                    "Utilisateur créé avec succès!",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    UserSerializer(user).data,
                    status.HTTP_201_CREATED)
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

    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        if request.user.is_staff is False:
            logger.warning(
                "vous ne pouvez modifier un utilisateur!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )

            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN
            )
        restaurant = request.user.restaurant
        try:
            user = get_user_model().objects.get(
                pk=kwargs['pk'],
                is_deleted=False,
                is_client=False,
                delivery=None,
                restaurant=restaurant
            )
        except User.DoesNotExist:
            logger.error(
                "utilisateur à modifier inexistant",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Utilisateur à modifier inexistant"},
                status.HTTP_404_NOT_FOUND
            )
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            if request.user.id == kwargs['pk']:
                if request.user.is_staff != serializer.validated_data['is_staff']:
                    logger.error(
                        "impossible de modifier son rôle toi même!",
                        extra={
                            'restaurant': request.user.restaurant,
                            'user': request.user.id
                        }
                    )
                    return Response(
                        {'message': 'impossible de modifier son rôle toi même'},
                        status=status.HTTP_409_CONFLICT)
            user = serializer.save()
            logger.info(
                "Utilisateur modifié avec succès!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(UserSerializer(user).data)
        else:
            logger.error(
                str(serializer.errors),
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        if request.user.is_staff is False:
            logger.warning(
                "Vous n'avez pas droit de supprimer un utilisateur!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN
            )
        restaurant = request.user.restaurant
        users = get_user_model().objects.all().filter(
            is_deleted=False,
            is_client=False,
            delivery=None,
            restaurant=restaurant
        ).order_by('id')
        list_users = list(users)
        user_ad = list_users[0]
        if kwargs['pk'] == user_ad.id:
            logger.error(
                "Vous ne pouvez supprimer l'utilisateur par défaut",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous ne pouvez supprimer l'utilisateur par défaut"},
                status=status.HTTP_409_CONFLICT)
        if request.user.id == kwargs['pk']:
            logger.error(
                "Conflit - Vous ne pouvez vous supprimer!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {'message': "Conflit - Vous ne pouvez vous supprimer!"},
                status=status.HTTP_409_CONFLICT)
        try:
            user = get_user_model().objects.get(
                pk=kwargs['pk'],
                is_deleted=False,
                is_client=False,
                delivery=None,
                restaurant=restaurant
            )
        except User.DoesNotExist:
            logger.error(
                "utilisateur inexistant!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "restaurant inexistant"
                },
                status.HTTP_404_NOT_FOUND
            )
        user.is_active = False
        user.is_deleted = True
        user.save()
        logger.info(
            "Utilisateur supprimé avec succès",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response({'message': "utilisateur supprimé"}, status=status.HTTP_204_NO_CONTENT)
