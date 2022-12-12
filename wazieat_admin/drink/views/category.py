import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from drink.models.category import DrinkCategory
from drink.serializers.category import DrinkCategorySerializer
from django.db import connection
from accounts.models.restaurant import Restaurant
from django.db.models import Q

logger = logging.getLogger("myLogger")


class DrinkCategoryViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    queryset = DrinkCategory.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = DrinkCategorySerializer

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.has_perm('drink.view_drinkcategory') is False and
                user.is_super() is False):
            logger.warning(
                "Vous n'avez pas accès à la liste des categories de boissons.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la liste des categories de boissons."},
                status=status.HTTP_403_FORBIDDEN)

        connection.set_schema_to_public()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Liste des categories de boissons renvoyés avec succès.",
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
        if (user.has_perm('drink.view_drinkcategory') is False or
                user.is_super() is False or
                user.restaurant is not None):
            logger.warning(
                "Vous n'avez pas accès à la visualisation d'un categorie de boissons.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la visualisation d'un categorie de boissons."},
                status=status.HTTP_403_FORBIDDEN)
        connection.set_schema_to_public()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(
            "Categorie de boissons renvoyé avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.has_perm('drink.add_drinkcategory') is False or
                user.is_super() is False or
                user.restaurant is not None):
            logger.warning(
                "Vous n'avez pas de droits pour ajouter une categorie de boissons.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour ajouter une categorie de boissons."},
                status=status.HTTP_403_FORBIDDEN)
        connection.set_schema_to_public()
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            keys_num = DrinkCategory.objects.all().filter(
                name=serializer.validated_data['name'],
                is_active=True,
                is_deleted=False).count()
            if keys_num >= 1:
                logger.error(
                    "Une categorie de boissons avec ce nom existe dejà",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Une categorie de boissons avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            logger.info(
                "Categorie de boissons créé avec succès",
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

    def perform_create(self, serializer):
        """Docstring for function."""
        serializer.save()

    @permission_classes([IsAuthenticated])
    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.has_perm('drink.change_drinkcategory') is False or
                user.is_super() is False or
                user.restaurant is not None):
            logger.warning(
                "Vous n'avez pas de droits pour modifier une categorie de boissons.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour modifier une categorie de boissons."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            connection.set_schema_to_public()
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            number = DrinkCategory.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Une categorie de boissons existe avec ce nom",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Une categorie de boissons existe avec ce nom"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            logger.info(
                "Mise à jour de la categorie de boissons réussie!",
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
        serializer.save()

    @permission_classes([IsAuthenticated])
    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.has_perm('drink.delete_drinkcategory') is False or
                user.is_super() is False or
                user.restaurant is not None):
            logger.warning(
                "Vous n'avez pas de droits pour supprimer une categorie de boissons.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour supprimer une categorie de boissons."},
                status=status.HTTP_403_FORBIDDEN)
        connection.set_schema_to_public()
        try:
            instance = DrinkCategory.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()
            count = Restaurant.objects.all().filter(
                drinkCategory=instance, is_active=True).count()
            if count == 0:
                self.perform_destroy(instance)
                logger.info(
                    "Categorie de boissons supprimé avec succès",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Categorie de boissons supprimé avec succès"},
                    status=status.HTTP_204_NO_CONTENT)
            else:
                logger.error(
                    "Cette categorie de boissons est liée aux restaurants",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Cette categorie de boissons est liée aux restaurants"},
                    status=status.HTTP_409_CONFLICT)
        except DrinkCategory.DoesNotExist:
            logger.info(
                "La categorie de boissons à supprimer n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "La categorie de boissons à supprimer n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
