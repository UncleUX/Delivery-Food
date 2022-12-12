import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from drink.models.drink import Drink
from django.db import connection
from rest_framework.parsers import MultiPartParser
from drink.serializers.drink import DrinkSerializer
from django.db.models import Q

logger = logging.getLogger("myLogger")


class DrinkViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    queryset = Drink.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = DrinkSerializer

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        connection.set_schema_to_public()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Liste des types de boissons renvoyés avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        connection.set_schema_to_public()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(
            "boisson renvoyée avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.is_super() is False:
            logger.warning(
                "Vous n'avez pas de droits pour ajouter une boisson",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour ajouter une boisson."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            connection.set_schema_to_public()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            keys_num = Drink.objects.all().filter(
                name=serializer.validated_data['name'],
                is_active=True,
                is_deleted=False).count()
            if keys_num >= 1:
                logger.error(
                    "Une boisson avec ce nom existe dejà",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Une boisson avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)
            self.perform_create(serializer, user=user)
            headers = self.get_success_headers(serializer.data)
            logger.info(
                "Boisson créée avec succès",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers)
        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)

    def perform_create(self, serializer, user):
        """Docstring for function."""
        connection.set_schema_to_public()
        serializer.save(created_by=user)

    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.is_super() is False:
            logger.warning(
                "Vous n'avez pas de droits pour modifier une boisson.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour modifier une boisson."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            connection.set_schema_to_public()
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            number = Drink.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Une boisson avec ce nom existe dejà",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Une boisson avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            logger.info(
                "Mise à jour de la boisson réussie!",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(serializer.data)

        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)

    def perform_update(self, serializer):
        """Docstring for function."""
        connection.set_schema_to_public()
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.is_super() is False:
            logger.warning(
                "Vous n'avez pas de droits pour supprimer une boisson.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour supprimer une boisson."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            connection.set_schema_to_public()
            instance = Drink.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()
            self.perform_destroy(instance)
            logger.info(
                "Boisson supprimée avec succès",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Boisson supprimée avec succès"},
                status=status.HTTP_204_NO_CONTENT)
        except DrinkPicture.DoesNotExist:
            logger.info(
                "La boisson à supprimer n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "La boisson à supprimer n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
