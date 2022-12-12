import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from food.models.food_picture import FoodPicture, FoodImage
from django.db import connection
from rest_framework.parsers import MultiPartParser
from food.serializers.food_picture import FoodPictureSerializer, FoodImageSerializer
from django.db.models import Q

logger = logging.getLogger("myLogger")


class FoodPictureViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    queryset = FoodPicture.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = FoodPictureSerializer

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('food.view_foodpicture') is False:
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
        if user.has_perm('food.view_foodpicture') is False:
            logger.warning(
                "Vous n'avez pas accès à la visualisation d'une boisson.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la visualisation d'une boisson."},
                status=status.HTTP_403_FORBIDDEN)
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
        if user.has_perm('food.add_foodpicture') is False:
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
            keys_num = FoodPicture.objects.all().filter(
                name=serializer.validated_data['name'],
                is_active=True,
                is_deleted=False).count()
            if keys_num >= 1:
                logger.error(
                    "Une photo de plat avec ce nom existe dejà",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Une photo de plat avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)
            self.perform_create(serializer, user=user)
            headers = self.get_success_headers(serializer.data)
            logger.info(
                "Photo de plat créée avec succès",
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
        if user.has_perm('food.change_foodpicture') is False:
            logger.warning(
                "Vous n'avez pas de droits pour modifier une photo de plat.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour modifier une photo de plat."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            connection.set_schema_to_public()
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            number = FoodPicture.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Une photo de plat avec ce nom existe dejà",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Une photo de plat avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            logger.info(
                "Mise à jour de la photo de plat réussie!",
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
        # connection.set_schema_to_public()
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('food.delete_foodpicture') is False:
            logger.warning(
                "Vous n'avez pas de droits pour supprimer une photo de plat.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour supprimer une photo de plat."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            connection.set_schema_to_public()
            instance = FoodPicture.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()
            self.perform_destroy(instance)
            logger.info(
                "Photo de plat supprimée avec succès",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Photo de plat supprimée avec succès"},
                status=status.HTTP_204_NO_CONTENT)
        except FoodPicture.DoesNotExist:
            logger.info(
                "La photo de plat à supprimer n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "La photo de plat à supprimer n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
