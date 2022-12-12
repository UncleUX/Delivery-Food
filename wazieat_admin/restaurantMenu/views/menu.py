import logging
import decimal
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from core.tenant import set_tenant
from restaurantMenu.serializers.menu import MenuSerializer
from restaurantMenu.models.menu import Menu
from django.db.models import Q

logger = logging.getLogger("myLogger")


class MenuViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    queryset = Menu.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = MenuSerializer

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantMenu.view_menu') is False:
            logger.warning(
                "Vous n'avez pas accès à la liste des menus",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la liste des menus"},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Liste des menus renvoyés avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantMenu.view_menu') is False:
            logger.warning(
                "Vous n'avez pas accès à la visualisation d'un menu.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la visualisation d'un menu."},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(
            "menu renvoyé avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantMenu.add_menu') is False:
            logger.warning(
                "Vous n'avez pas de droits pour ajouter un menu",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour ajouter un menu"},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            keys_num = Menu.objects.all().filter(
                name=serializer.validated_data['name'],
                is_active=True,
                is_deleted=False).count()
            if keys_num >= 1:
                logger.error(
                    "Un menu avec ce nom existe dejà",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Un menu avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)

            if (serializer.validated_data['status_price'] == 2 and
                    serializer.validated_data['real_price'] is None):
                logger.error(
                    "Vous devez renseigner un prix au menu",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Vous devez renseigner un prix au menu"},
                    status=status.HTTP_409_CONFLICT)

            menu = self.perform_create(serializer, user=user)
            price = 0
            for f in menu.foods.all():
                price = price + f.price
            for f in menu.drinks.all():
                price = price + f.price
            menu.calculated_price = price
            if menu.status_price == 1:
                if menu.percent is not None:
                    percent = menu.percent
                    if menu.percent < 0:
                        menu.real_price = price - (price*abs(percent)/100)
                    else:
                        menu.real_price = price + (price*abs(percent)/100)
            else:
                menu.real_price = price
            menu.save()
            headers = self.get_success_headers(serializer.data)

            logger.info(
                "Menu créé avec succès",
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
        return serializer.save(created_by=user, real_price=0)

    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantMenu.change_menu') is False:
            logger.warning(
                "Vous n'avez pas de droits pour modifier un menu.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour modifier un menu"},
                status=status.HTTP_403_FORBIDDEN)
        try:
            set_tenant(request)
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            number = Menu.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Un menu existe avec ce nom",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Un menu existe avec ce nom"},
                    status=status.HTTP_409_CONFLICT)

            menu = self.perform_update(serializer)
            price = 0
            for f in menu.foods.all():
                price = price + f.price
            for f in menu.drinks.all():
                price = price + f.price
            menu.calculated_price = price
            if menu.status_price == 1:
                if menu.percent is not None:
                    percent = decimal.Decimal(menu.percent)
                    if menu.percent < 0:
                        menu.real_price = price - (price*abs(percent)/100)
                    else:
                        menu.real_price = price + (price*abs(percent)/100)

            menu.save()
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            logger.info(
                "Mise à jour du menu réussie!",
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
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantMenu.delete_menu') is False:
            logger.warning(
                "Vous n'avez pas de droits pour supprimer un menu.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour supprimer un menu."},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        try:
            instance = Menu.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()

            self.perform_destroy(instance)
            return Response(
                {'message': "Menu supprimé avec succès"},
                status=status.HTTP_204_NO_CONTENT)

        except Menu.DoesNotExist:
            logger.info(
                "Le menu à supprimer n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Le menu à supprimer n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
