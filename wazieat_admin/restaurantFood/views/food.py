import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from accounts.models.user import User
from restaurantFood.models.food import RestaurantFood
from restaurantFood.models.ingredient import Ingredient
from rest_framework.parsers import MultiPartParser
from accounts.serializers.user import UserSerializer
from notifications.notification_admin_food import notifications_admin_food
from restaurantFood.serializers.food import RestaurantFoodSerializer, ViewRestaurantFoodSerializer
from accounts.models.restaurant import Restaurant
from core.tenant import set_tenant
from django.db.models import Q

from restaurantFood.utils import *

logger = logging.getLogger("myLogger")


class RestaurantFoodViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    queryset = RestaurantFood.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = RestaurantFoodSerializer
    parser_classes = [MultiPartParser]

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.view_restaurantfood') is False:
            logger.warning(
                "Vous n'avez pas accès à la liste des plats",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la liste des plats"},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        name = request.query_params.get('name', None)
        typ = request.query_params.get('type', None)
        if name is not None and typ is not None:
            queryset = RestaurantFood.objects.all().filter(
                name__icontains=name, foodType__name__icontains=typ, is_deleted=False).order_by('id')
        elif name is not None:
            queryset = RestaurantFood.objects.all().filter(
                name__icontains=name, is_deleted=False).order_by('id')
        elif typ is not None:
            queryset = RestaurantFood.objects.all().filter(
                foodType__name__icontains=typ, is_deleted=False).order_by('id')
        else:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        results = []
        ser = list(zip(queryset, serializer.data))
        for ind in ser:
            data = get_food(ind[0], ind[1]['foodPicture'])
            results.append(data)
        logger.info(
            "Liste des plats renvoyés avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(results)

    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.view_restaurantfood') is False:
            logger.warning(
                "Vous n'avez pas accès à la visualisation d'un plat.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la visualisation d'un plat."},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = get_food(instance, serializer.data['foodPicture'])
        logger.info(
            "Plat renvoyée avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(data)

    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.add_restaurantfood') is False:
            logger.warning(
                "Vous n'avez pas de droits pour ajouter un plat",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour ajouter un plat"},
                status=status.HTTP_403_FORBIDDEN)
        try:
            set_tenant(request)
            serializer = ViewRestaurantFoodSerializer(data=request.data)
            serializer_data = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer_data.is_valid(raise_exception=True)
            keys_num = RestaurantFood.objects.all().filter(
                name=serializer.validated_data['name'],
                is_deleted=False).count()
            if keys_num >= 1:
                logger.error(
                    "Un plat avec ce nom existe dejà",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Un plat avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)

            picture = None
            picture_rel = None
            try:
                picture = serializer.validated_data['foodPicture']
            except KeyError:
                try:
                    picture_rel = serializer.validated_data['foodPicture_related']
                except KeyError:
                    logger.error(
                        "Vous devez renseigner au moins un champ foodPicture ou foodPicture_related",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {'message': "Vous devez renseigner au moins un champ foodPicture ou foodPicture_related"},
                        status=status.HTTP_400_BAD_REQUEST)

            if picture is None and picture_rel is None:
                logger.error(
                    "L'un de ses champs foodPicture ou foodPicture_related ne doit pas être null",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "L'un de ses champs foodPicture ou foodPicture_related ne doit pas être null"},
                    status=status.HTTP_400_BAD_REQUEST)

            # gestion des ingrédients
            ingredients = []
            for ing in serializer.validated_data['ingredients']:
                keys_num = Ingredient.objects.all().filter(
                    name=ing,
                    is_deleted=False)
                if len(keys_num) == 1:
                    ingredients.append(keys_num[0])
                else:
                    val = Ingredient()
                    val.name = ing
                    val.description = "description"
                    val.quantity = "1 kg"
                    val.created_by = request.user
                    val.save()
                    ingredients.append(val)

            serializer_data.validated_data['ingredients'] = ingredients

            if picture is not None:
                serializer_data.validated_data['foodPicture_related'] = None
                objet = self.perform_create(serializer_data, user=user, is_active=True)
            else:
                objet = self.perform_create(serializer_data, user=user, is_active=True)

            data = get_food(objet, serializer_data.data['foodPicture'])
            headers = self.get_success_headers(serializer_data.data)

            logger.info(
                "Plat créé avec succès",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                data,
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

    def perform_create(self, serializer, user, is_active=None):
        """Docstring for function."""
        set_tenant(self.request)
        return serializer.save(created_by=user, is_active=is_active)

    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.change_restaurantfood') is False:
            logger.warning(
                "Vous n'avez pas de droits pour modifier un plat",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour modifier un plat"},
                status=status.HTTP_403_FORBIDDEN)
        try:
            set_tenant(request)
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = ViewRestaurantFoodSerializer(
                instance, data=request.data,
                partial=partial)
            serializer_data = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer_data.is_valid(raise_exception=True)
            number = RestaurantFood.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Un plat existe avec ce nom",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Un plat existe avec ce nom"},
                    status=status.HTTP_409_CONFLICT)

            category = None
            picture_rel = None
            try:
                picture_rel = serializer.validated_data['foodPicture_related']
            except KeyError:
                pass
            """
            if picture is None and picture_rel is None:
                logger.error(
                    "L'un de ses champs foodPicture ou foodPicture_related ne doit pas être null",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "L'un de ses champs foodPicture ou foodPicture_related ne doit pas être null"},
                    status=status.HTTP_400_BAD_REQUEST)
            """
            # gestion des ingrédients
            ingredients = []
            for ing in serializer.validated_data['ingredients']:
                keys_num = Ingredient.objects.all().filter(
                    name=ing,
                    is_deleted=False)
                if len(keys_num) == 1:
                    ingredients.append(keys_num[0])
                else:
                    val = Ingredient()
                    val.name = ing
                    val.description = "description"
                    val.quantity = "1 kg"
                    val.created_by = request.user
                    val.save()
                    ingredients.append(val)

            serializer_data.validated_data['ingredients'] = ingredients

            if picture_rel is None:
                if serializer_data.validated_data['foodPicture'] is None:
                    serializer_data.validated_data['foodPicture'] = instance.foodPicture
                # serializer_data.validated_data['is_active'] = False
                objet = self.perform_update(serializer_data)
            else:
                serializer_data.validated_data['foodPicture'] = None
                # serializer_data.validated_data['is_active'] = True
                objet = self.perform_update(serializer_data)

            data = get_food(objet, serializer_data.data['foodPicture'])
            if getattr(objet, '_prefetched_objects_cache', None):
                objet._prefetched_objects_cache = {}

            logger.info(
                "Mise à jour du plat réussie!",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(data)

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
        set_tenant(self.request)
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantFood.delete_restaurantfood') is False:
            logger.warning(
                "Vous n'avez pas de droits pour supprimer un plat.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour supprimer un plat."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            set_tenant(request)
            instance = RestaurantFood.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()
            self.perform_destroy(instance)
            logger.info(
                "Plat supprimé avec succès",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Plat supprimé avec succès"},
                status=status.HTTP_204_NO_CONTENT)
        except RestaurantFood.DoesNotExist:
            logger.info(
                "Le plat à supprimer n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Le plat à supprimer n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        set_tenant(self.request)
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
