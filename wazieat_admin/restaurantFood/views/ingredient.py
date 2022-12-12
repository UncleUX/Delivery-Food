import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from restaurantFood.models.ingredient import Ingredient
from core.tenant import set_tenant
from restaurantFood.serializers.ingredient import IngredientSerializer
from restaurantFood.models.food import RestaurantFood
from django.db.models import Q

logger = logging.getLogger("myLogger")


class IngredientViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    queryset = Ingredient.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = IngredientSerializer

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.view_ingredient') is False:
            logger.warning(
                "Vous n'avez pas accès à la liste des ingredients",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la liste des ingredients"},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Liste des ingredients renvoyés avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.view_ingredient') is False:
            logger.warning(
                "Vous n'avez pas accès à la visualisation d'un ingredient.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la visualisation d'un ingredient."},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(
            "Ingredient renvoyé avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.add_ingredient') is False:
            logger.warning(
                "Vous n'avez pas de droits pour ajouter un ingredient",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour ajouter un ingredient"},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            keys_num = Ingredient.objects.all().filter(
                name=serializer.validated_data['name'],
                is_active=True,
                is_deleted=False).count()
            if keys_num >= 1:
                logger.error(
                    "Un ingredient avec ce nom existe dejà",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Un ingredient avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_create(serializer, user=user)
            headers = self.get_success_headers(serializer.data)

            logger.info(
                "Ingredient créé avec succès",
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
        set_tenant(self.request)
        serializer.save(created_by=user)

    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.change_ingredient') is False:
            logger.warning(
                "Vous n'avez pas de droits pour modifier un ingredient.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour modifier un ingredient."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            set_tenant(request)
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            number = Ingredient.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Un ingredient existe avec ce nom",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Un ingredient existe avec ce nom"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            logger.info(
                "Mise à jour de l'ingredient réussie!",
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

    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.delete_ingredient') is False:
            logger.warning(
                "Vous n'avez pas de droits pour supprimer un ingredient.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour supprimer un ingredient."},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        try:
            instance = Ingredient.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()
            objets = RestaurantFood.ingredients.all()
            if instance not in objets:
                self.perform_destroy(instance)
                logger.info(
                    "Ingredient supprimé avec succès",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Ingredient supprimé avec succès"},
                    status=status.HTTP_204_NO_CONTENT)
            else:
                logger.error(
                    "Cet ingredient est lié à un plat",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Cet ingredient est lié à un plat"},
                    status=status.HTTP_409_CONFLICT)
        except Ingredient.DoesNotExist:
            logger.info(
                "L'ingredient à supprimer n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "L'ingredient à supprimer n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
