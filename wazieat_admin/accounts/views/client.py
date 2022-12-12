import logging
from uuid import uuid4
import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from core.pagination import CustomPageNumberPagination
from notifications.notifications import notifications
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.contrib.auth import get_user_model
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from accounts.serializers.user import UserPasswordSerializer
from core.schemas.schema_client import schema_response_client
from restaurantCommande.models.commande import Commande
from accounts.serializers.client import ClientSerializer, ClientUpdateSerializer, ClientCreateSerializer
from accounts.models.restaurant import Restaurant
from accounts.models.user import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")


correct_response = openapi.Response(
    description='Client',
    schema=schema_response_client,)
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


class ClientViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    queryset = User.objects.all().filter(
                is_deleted=False,
                restaurant=None,
                is_client=True).order_by('last_name')
    serializer_class = ClientSerializer

    @permission_classes([IsAuthenticated])
    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.is_super() is False and
                user.has_perm('accounts.view_user') is False):
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
        queryset = self.filter_queryset(self.get_queryset())
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

    @permission_classes([IsAuthenticated])
    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.is_super() is False and
                user.client is False and
                user.has_perm('accounts.view_user') is False):
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
        if user.client is True and user.id != kwargs['pk']:
            logger.warning(
                "Vous ne pouvez pas visualiser les informations d'un autre client",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous ne pouvez pas visualiser les informations d'un autre client"},
                status.HTTP_403_FORBIDDEN
            )
        connection.set_schema_to_public()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(
            "détail sur le client renvoyé avec succès!",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ClientCreateSerializer,
                         responses={200: correct_response, 400: bad_request, 412: error_response})
    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                client = self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                reset_token = uuid4()
                client.reset_token = reset_token
                client.password_requested_at = datetime.datetime.now()
                client.is_staff = False
                client.is_admin = False
                client.is_client = True
                client.save()
                notifications(request, client)
                logger.info(
                    "Client créé avec succès!",
                    extra={
                        'restaurant': client.restaurant,
                        'user': client.id
                    }
                )
                return Response(
                    serializer.data,
                    status.HTTP_201_CREATED,
                    headers=headers)
        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': None,
                    'user': None
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)

    def perform_create(self, serializer):
        """Docstring for function."""
        return serializer.save()

    @permission_classes([IsAuthenticated])
    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        if (request.user.is_super() is False and
                request.user.is_client is False and
                request.user.has_perm('accounts.change_user') is False):
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
        if request.user.is_client is True and request.user.id != kwargs['pk']:
            logger.error(
                "Vous ne pouvez pas modifier les informations d'un autre client",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )

            return Response(
                {"message": "Vous ne pouvez pas modifier les informations d'un autre client"},
                status.HTTP_404_NOT_FOUND
            )
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data,
            partial=partial)
        if serializer.is_valid() is True:
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            logger.info(
                "Client modifié avec succès!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(serializer.data)
        else:
            logger.error(
                str(serializer.errors),
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        """Docstring for function."""
        return serializer.save()

    @permission_classes([IsAuthenticated])
    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.is_super() is False and
                user.is_client is False and
                user.has_perm('accounts.delete_user') is False):
            logger.warning(
                "Vous n'avez pas les droits nécessaires!",
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
        if user.is_client is True and user.id != int(kwargs['pk']):
            logger.warning(
                "Vous ne pouvez pas supprimer le compte d'un autre client",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous ne pouvez pas supprimer le compte d'un autre client"},
                status.HTTP_403_FORBIDDEN
            )

        instance = self.get_object()
        restaurants = Restaurant.objects.all().order_by('id')
        count = None
        for restau in restaurants:
            set_tenant_from_restaurant(restau)
            count = Commande.objects.all().filter(
                ~Q(status=5), created_by=instance).count()
            if count != 0:
                break
        if count == 0:
            instance.delete()
            logger.info(
                "Client supprimé avec succès",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                status=status.HTTP_204_NO_CONTENT)
        else:
            logger.error(
                "Ce client à une ou des commandes non livrées",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Ce client à une ou des commandes non livrées"},
                status=status.HTTP_409_CONFLICT)
