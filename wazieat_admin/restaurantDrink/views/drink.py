import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from restaurantDrink.models.drink import RestaurantDrink
from rest_framework.parsers import MultiPartParser
from restaurantDrink.serializers.drink import RestaurantDrinkSerializer
from core.tenant import set_tenant
from django.db.models import Q
from restaurantDrink.utils import *

logger = logging.getLogger("myLogger")


class RestaurantDrinkViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    queryset = RestaurantDrink.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = RestaurantDrinkSerializer
    parser_classes = [MultiPartParser]

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantDrink.view_restaurantdrink') is False:
            logger.warning(
                "Vous n'avez pas accès à la liste des boissons",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la liste des boissons"},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        name = request.query_params.get('name', None)
        typ = request.query_params.get('type', None)
        if name is not None and typ is not None:
            queryset = RestaurantDrink.objects.all().filter(
                name__icontains=name, drinkType__name__icontains=typ, is_deleted=False).order_by('id')
        elif name is not None:
            queryset = RestaurantDrink.objects.all().filter(
                name__icontains=name, is_deleted=False).order_by('id')
        elif typ is not None:
            queryset = RestaurantDrink.objects.all().filter(
                drinkType__name__icontains=typ, is_deleted=False).order_by('id')
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
            data = get_drink(ind[0], ind[1]['drinkPicture'])
            results.append(data)
        logger.info(
            "Liste des types de boissons renvoyés avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(results)

    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantDrink.view_restaurantdrink') is False:
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
        set_tenant(request)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = get_drink(instance, serializer.data['drinkPicture'])
        logger.info(
            "boisson renvoyée avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(data)

    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantDrink.add_restaurantdrink') is False:
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
            set_tenant(request)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            keys_num = RestaurantDrink.objects.all().filter(
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
            admin_drink = None
            drinkCategory = None
            drinkType = None
            try:
                admin_drink = serializer.validated_data['admin_drink']
            except KeyError:
                try:
                    drinkCategory = serializer.validated_data['drinkCategory']
                    drinkType = serializer.validated_data['drinkType']
                except KeyError:
                    logger.error(
                        "Vous devez renseigner au moins un champ drinkCategory/drinkType ou admin_drink",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {'message': "Vous devez renseigner au moins un champ drinkCategory/drinkType ou admin_drink"},
                        status=status.HTTP_400_BAD_REQUEST)
            if admin_drink is not None:
                serializer.validated_data['drinkCategory'] = None
                serializer.validated_data['drinkType'] = None
                serializer.validated_data['drinkPicture'] = None

            instance = self.perform_create(serializer, user=user)
            headers = self.get_success_headers(serializer.data)
            data = get_drink(instance, serializer.data['drinkPicture'])
            logger.info(
                "Boisson créée avec succès",
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

    def perform_create(self, serializer, user):
        """Docstring for function."""
        set_tenant(self.request)
        return serializer.save(created_by=user)

    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantDrink.change_restaurantdrink') is False:
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
            set_tenant(request)
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            number = RestaurantDrink.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Une boisson existe avec ce nom",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Une boisson existe avec ce nom"},
                    status=status.HTTP_409_CONFLICT)
            admin_drink = None
            drinkCategory = None
            drinkType = None
            try:
                admin_drink = serializer.validated_data['admin_drink']
            except KeyError:
                try:
                    drinkCategory = serializer.validated_data['drinkCategory']
                    drinkType = serializer.validated_data['drinkType']
                except KeyError:
                    logger.error(
                        "Vous devez renseigner au moins un champ drinkCategory/drinkType ou admin_drink",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {'message': "Vous devez renseigner au moins un champ drinkCategory/drinkType ou admin_drink"},
                        status=status.HTTP_400_BAD_REQUEST)
            if admin_drink is not None:
                serializer.validated_data['drinkCategory'] = None
                serializer.validated_data['drinkType'] = None
                serializer.validated_data['drinkPicture'] = None
            else:
                if serializer.validated_data['drinkPicture'] is None:
                    serializer.validated_data['drinkPicture'] = instance.drinkPicture

            instance = self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            data = get_drink(instance, serializer.data['drinkPicture'])
            logger.info(
                "Mise à jour de la boisson réussie!",
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
        if user.has_perm('restaurantDrink.delete_restaurantdrink') is False:
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
            set_tenant(request)
            instance = RestaurantDrink.objects.filter(
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
        except RestaurantDrink.DoesNotExist:
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
        set_tenant(self.request)
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
