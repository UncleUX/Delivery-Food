import logging
from uuid import uuid4
import datetime
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status, viewsets
from django.contrib.auth import get_user_model
from core.pagination import CustomPageNumberPagination
from notifications.notifications import notifications
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from django.conf import settings
from django.db import connection
from restaurantCommande.models.commande import Commande
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from core.schemas.schema_delivery import schema_response_delivery
from accounts.serializers.delivery import DeliverySerializer, DeliveryCreateSerializer
from accounts.models.restaurant import Restaurant
from accounts.models.user import User
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Créer un commentaire sur un menu du restaurant',
    schema=schema_response_delivery,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


class DeliveryViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    queryset = User.objects.all().filter(
                is_deleted=False,
                restaurant=None,
                delivery__isnull=False).order_by('id')
    serializer_class = DeliverySerializer

    @swagger_auto_schema(responses={403: forbidden_request})
    @permission_classes([IsAuthenticated])
    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.is_super() is False and
                user.has_perm('accounts.view_delivery') is False):
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
            "Liste des livreurs renvoyées avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )

        return Response(serializer.data)

    @swagger_auto_schema(responses={403: forbidden_request})
    @permission_classes([IsAuthenticated])
    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.is_super() is False and
                user.delivery is None and
                user.has_perm('accounts.view_delivery') is False):
            logger.warning(
                "Vous n'avez pas les droits nécessaires!",
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
        if user.delivery is not None and user.id != kwargs['pk']:
            logger.warning(
                "Vous ne pouvez pas visualiser les informations d'un autre livreur",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous ne pouvez pas visualiser les informations d'un autre livreur"
                },
                status.HTTP_403_FORBIDDEN
            )
        connection.set_schema_to_public()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(
            "détail sur le livreur renvoyé avec succès!",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response(serializer.data)

    @swagger_auto_schema(request_body=DeliveryCreateSerializer)
    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        try:
            serializer = DeliverySerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                if serializer.validated_data['delivery']['has_motor'] is True:
                    try:
                        brand = serializer.validated_data['delivery']['brand']
                        model = serializer.validated_data['delivery']['model']
                        power = serializer.validated_data['delivery']['power']
                        year_motor = serializer.validated_data['delivery']['year_motor']
                    except KeyError:
                        logger.error(
                            "Vous devez renseigner les champs brand, model, power, year_motor",
                            extra={
                                'restaurant': None,
                                'user': None
                            }
                        )
                        return Response(
                            {"Vous devez renseigner les champs brand, model, power, year_motor"},
                            status.HTTP_400_BAD_REQUEST
                        )

                delivery = self.perform_create(serializer)

                headers = self.get_success_headers(serializer.data)

                reset_token = uuid4()
                delivery.reset_token = reset_token
                delivery.password_requested_at = datetime.datetime.now()
                delivery.is_staff = False
                delivery.is_active = False
                delivery.is_admin = False
                delivery.save()
                notifications(request, delivery)
                # admin = User.objects.get(is_active=True, is_deleted=False, is_admin=True, is_staff=True)
                # name = delivery.first_name + " " + delivery.last_name
                # notifications_admin(request, admin, "livreur", name, delivery.email)
                logger.info(
                    "Livreur créé avec succès!",
                    extra={
                        'restaurant': delivery.restaurant,
                        'user': delivery.id
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
                request.user.delivery is None and
                request.user.has_perm('accounts.change_delivery') is False):
            logger.warning(
                "Vous n'avez pas les droits nécessaires!",
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
        if request.user.delivery is not None and request.user.id != kwargs['pk']:
            logger.error(
                "Vous ne pouvez pas modifier les informations d'un autre livreur",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )

            return Response(
                {
                    "message": "Vous ne pouvez pas modifier les informations d'un autre livreur"
                },
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
                "Livreur modifié avec succès!",
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
                user.delivery is None and
                user.has_perm('accounts.delete_delivery') is False):
            logger.warning(
                "Vous n'avez pas les droits nécessaires!",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {
                    "message": "Vous n'avez pas les droits nécessaires"
                },
                status.HTTP_403_FORBIDDEN
            )
        connection.set_schema_to_public()
        if user.delivery is not None and user.id != kwargs['pk']:
            logger.warning(
                "Vous ne pouvez pas supprimer le compte d'un autre livreur",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous ne pouvez pas supprimer le compte d'un autre livreur"
                },
                status.HTTP_403_FORBIDDEN
            )

        instance = self.get_object()
        restaurants = Restaurant.objects.all().order_by('id')
        count = None
        for restau in restaurants:
            set_tenant_from_restaurant(restau)
            count = Commande.objects.all().filter(
                ~Q(status=5), delivery_validated_by=instance).count()
            if count != 0:
                break
        if count == 0:
            instance.delete()
            logger.info(
                "Livreur supprimé avec succès",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                status=status.HTTP_204_NO_CONTENT)
        else:
            logger.error(
                "Ce livreur à des commandes non livrées",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Ce livreur à des commandes non livrées"},
                status=status.HTTP_409_CONFLICT)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()

