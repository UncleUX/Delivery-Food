import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from core.tenant import set_tenant
from restaurantMenu.serializers.publicationPeriod import PublicationPeriodSerializer
from restaurantMenu.models.publicationPeriod import PublicationPeriod
from restaurantMenu.models.menu import Menu
from django.db.models import Q

logger = logging.getLogger("myLogger")


class PublicationPeriodViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    queryset = PublicationPeriod.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = PublicationPeriodSerializer

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantMenu.view_publicationperiod') is False:
            logger.warning(
                "Vous n'avez pas accès à la liste des periodes de publication",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la liste des periodes de publication"},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Liste des periodes de publication renvoyés avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantMenu.view_publicationperiod') is False:
            logger.warning(
                "Vous n'avez pas accès à la visualisation d'une periode de publication.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la visualisation d'une periode de publication."},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(
            "periode de publication renvoyée avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantMenu.add_publicationperiod') is False:
            logger.warning(
                "Vous n'avez pas de droits pour ajouter une periode de publication",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour ajouter une periode de publication"},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            keys_num = PublicationPeriod.objects.all().filter(
                name=serializer.validated_data['name'],
                is_active=True,
                is_deleted=False).count()
            if keys_num >= 1:
                logger.error(
                    "Une periode de publication avec ce nom existe dejà",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Une periode de publication avec ce nom existe dejà"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_create(serializer, user=user)
            headers = self.get_success_headers(serializer.data)

            logger.info(
                "periode de publication créée avec succès",
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
        if user.has_perm('restaurantMenu.change_publicationperiod') is False:
            logger.warning(
                "Vous n'avez pas de droits pour modifier une periode de publication.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour modifier une periode de publication."},
                status=status.HTTP_403_FORBIDDEN)
        try:
            set_tenant(request)
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)
            number = PublicationPeriod.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Une periode de publication existe avec ce nom",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Une periode de publication existe avec ce nom"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            logger.info(
                "Mise à jour de la periode de publication réussie!",
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
        if user.has_perm('restaurantMenu.delete_publicationperiod') is False:
            logger.warning(
                "Vous n'avez pas de droits pour supprimer une periode de publication.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour supprimer une periode de publication."},
                status=status.HTTP_403_FORBIDDEN)
        set_tenant(request)
        try:
            instance = PublicationPeriod.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()
            number = Menu.objects.all().filter(
                period=instance,
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Un menu est lié a cette periode de publication",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Un menu est lié a cette periode de publication"},
                    status=status.HTTP_409_CONFLICT)
            self.perform_destroy(instance)
            return Response(
                {'message': "periode de publication supprimée avec succès"},
                status=status.HTTP_204_NO_CONTENT)

        except PublicationPeriod.DoesNotExist:
            logger.info(
                "La periode de publication à supprimer n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "La periode de publication à supprimer n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
