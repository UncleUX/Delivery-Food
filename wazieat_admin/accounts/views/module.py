import logging
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework import status, viewsets
from accounts.serializers.module import ModuleSerializer
from accounts.models.module import Module
from django.db import connection
from accounts.models.restaurant import Restaurant
from django.db.models import Q

logger = logging.getLogger("myLogger")


class ModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Module.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = ModuleSerializer

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()

        if request.user.is_super() is False:
            logger.error(
                "Vous n'avez pas accès à la liste des modules de wazieats",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous n'avez pas les droits nécessaires",
                }, status.HTTP_403_FORBIDDEN)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Liste des modules renvoyé avec succès.",
            extra={
                'restaurant': None,
                'user': request.user.id
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        if request.user.is_super() is False:
            logger.error(
                "Vous n'avez pas accès à la visualisation d'un module wazieats",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous n'avez pas les droits nécessaires",
                }, status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(
            "Module renvoyé avec succès.",
            extra={
                'restaurant': None,
                'user': request.user.id
            }
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        if request.user.is_super() is False:
            logger.error(
                "Vous n'avez pas accès à la creation d'un module wazieats",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous n'avez pas les droits nécessaires",
                }, status.HTTP_403_FORBIDDEN)
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            keys_num = Module.objects.all().filter(
                name=serializer.validated_data['name'],
                is_active=True,
                is_deleted=False).count()
            if keys_num >= 1:
                logger.error(
                    "Un module avec ce nom existe dejà",
                    extra={
                        'restaurant': None,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Un module avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            logger.info(
                "Module créé avec succès",
                extra={
                    'restaurant': None,
                    'user': request.user.id
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
                    'restaurant': None,
                    'user': request.user.id
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)

    def perform_create(self, serializer):
        """Docstring for function."""
        serializer.save()

    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        if request.user.is_super() is False:
            logger.error(
                "Vous n'avez pas accès à la modification d'un module wazieats",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous n'avez pas les droits nécessaires",
                }, status.HTTP_403_FORBIDDEN)
        try:
            connection.set_schema_to_public()
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            number = Module.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Un module existe avec ce nom",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Un module existe avec ce nom"},
                    status=status.HTTP_409_CONFLICT)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            logger.info(
                "Mise à jour module réussie!",
                extra={
                    'restaurant': None,
                    'user': request.user.id
                }
            )
            return Response(serializer.data)

        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': None,
                    'user': request.user.id
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
        if request.user.is_super() is False:
            logger.error(
                "Vous n'avez pas accès à la liste des wazieats",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous n'avez pas les droits nécessaires",
                }, status.HTTP_403_FORBIDDEN)
        connection.set_schema_to_public()
        try:
            instance = Module.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()
            count = Restaurant.objects.all().filter(
                module=instance).count()
            if count == 0:
                self.perform_destroy(instance)
                logger.info(
                    "Module supprimé avec succès",
                    extra={
                        'restaurant': None,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Module supprimé avec succès"},
                    status=status.HTTP_204_NO_CONTENT)
            else:
                logger.error(
                    "Ce module est lié aux wazieats",
                    extra={
                        'restaurant': None,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Ce module est lié aux wazieats"},
                    status=status.HTTP_409_CONFLICT)
        except Module.DoesNotExist:
            logger.info(
                "Le module à supprimer n'existe pas",
                extra={
                    'restaurant': None,
                    'user': request.user.id
                }
            )
            return Response(
                {'message': "Le module à supprimer n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
