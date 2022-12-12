import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
from rest_framework import status, viewsets
from django.db import connection
from django.contrib.auth import get_user_model
from core.schemas.schema_user import schema_response_user
from accounts.serializers.role import RoleSerializer, RoleCreateSerializer
from accounts.serializers.user import UserSerializer
from accounts.models.role import Role
from accounts.models.user import User
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


logger = logging.getLogger("myLogger")

schema_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", type=openapi.TYPE_INTEGER, description="Identifiant"),
        "name": openapi.Schema(title="name", type=openapi.TYPE_INTEGER, description="Nom"),
        "permissions": openapi.Schema(title="description", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description="Permissions"),
        "description": openapi.Schema(title="permissions", type=openapi.TYPE_INTEGER, description="Description"),
        "users": schema_response_user
    }
)
correct_response = openapi.Response(
    description='Role',
    schema=schema_response,)
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')
forbidden_request = openapi.Response('Pas de permissions')


class RoleViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    queryset = Role.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if request.user.is_staff is False:
            logger.error(
                "Vous n'avez pas accès à la liste des roles",
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
        queryset = Role.objects.all().filter(
            restaurant=request.user.restaurant,
            is_deleted=False
        )
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        data = []
        for d in serializer.data:
            s = {
                "id": d['id'],
                "name": d['name'],
                "permissions": d['permissions'],
                "is_active": d['is_active'],
                "description": d['description'],
                "reference": d['reference'],
                "users": UserSerializer(User.objects.filter(roles__name=d['name']), many=True).data
            }
            data.append(s)
        logger.info(
            "Liste des rôles renvoyées avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )

        return Response(data)

    @swagger_auto_schema(responses={403: forbidden_request, 200: correct_response})
    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if (user.is_super() is False and
                user.has_perm('accounts.view_role') is False):
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
        connection.set_schema_to_public()
        try:
            instance = Role.objects.all().filter(
                pk=kwargs['pk'],
                restaurant=request.user.restaurant,
                is_deleted=False
            ).get()
        except Role.DoesNotExist:
            logger.info(
                "Role inexistant!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"detail": "Pas trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        data = {
            "id": serializer.data['id'],
            "name": serializer.data['name'],
            "permissions": serializer.data['permissions'],
            "is_active": serializer.data['is_active'],
            "description": serializer.data['description'],
            "reference": serializer.data['reference'],
            "users": UserSerializer(User.objects.filter(roles__name=serializer.data['name']), many=True).data
        }
        logger.info(
            "détail sur le rôle renvoyé avec succès!",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response(data)

    @swagger_auto_schema(request_body=RoleCreateSerializer,
                         responses={403: forbidden_request, 200: correct_response, 400: bad_request, 412: error_response})
    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        if request.user.is_staff is False:
            logger.error(
                "Vous n'avez pas accès pour créer un role",
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
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            restaurant = request.user.restaurant
            try:
                ids = request.data['users']
            except KeyError:
                logger.error(
                    "L'attribut users manquant",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response({
                    "message": "L'attribut users manquant"},
                    status.HTTP_400_BAD_REQUEST)
            users_add = []
            for ide in ids:
                try:
                    user = get_user_model().objects.get(
                        pk=ide,
                        restaurant=restaurant,
                        is_deleted=False)
                    users_add.append(user)
                except User.DoesNotExist:
                    logger.error(
                        "Utilisateur inexistant!",
                        extra={
                            'restaurant': request.user.restaurant,
                            'user': request.user.id
                        }
                    )
                    return Response(
                        {
                            "message": "Utilisateur inexistant"
                        },
                        status.HTTP_404_NOT_FOUND
                    )
            number = Role.objects.all().filter(
                name=serializer.validated_data['name'],
                restaurant=restaurant,
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Un role avec ce nom existe déjà",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Un role avec ce nom existe déjà"},
                    status=status.HTTP_409_CONFLICT)

            role = serializer.save(restaurant=restaurant)
            for user in users_add:
                user.roles.add(role)
                user.save()

            data = {
                "id": serializer.data['id'],
                "name": serializer.data['name'],
                "permissions": serializer.data['permissions'],
                "is_active": serializer.data['is_active'],
                "description": serializer.data['description'],
                "reference": serializer.data['reference'],
                "users": UserSerializer(users_add, many=True).data
            }
            logger.info(
                "Role ajouté avec succès.",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)

    def perform_create(self, serializer):
        """Docstring for function."""
        return serializer.save()

    @swagger_auto_schema(request_body=RoleCreateSerializer,
                         responses={403: forbidden_request, 200: correct_response, 400: bad_request, 412: error_response})
    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        connection.set_schema_to_public()
        if request.user.is_staff is False:
            logger.error(
                "Vous n'avez pas accès à la modification d'un rôle",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN)
        try:
            role = Role.objects.get(
                pk=kwargs['pk'],
                restaurant=request.user.restaurant,
                is_deleted=False
            )
        except Role.DoesNotExist:
            logger.error(
                "Role utilisateur inexistant!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Rôle inexistant"},
                status.HTTP_404_NOT_FOUND
            )

        restaurant = request.user.restaurant
        serializer = RoleSerializer(role, data=request.data)
        try:
            ids = request.data['users']
        except KeyError:
            logger.error(
                "L'attribut users manquant",
                extra={
                    'restaurant': restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "L'attribut users manquant"},
                status.HTTP_400_BAD_REQUEST)
        users_add = []
        for ide in ids:
            try:
                user = get_user_model().objects.get(
                    pk=ide,
                    restaurant=restaurant,
                    is_deleted=False)
                users_add.append(user)
            except User.DoesNotExist:
                logger.error(
                    "Utilisateur inexistant!",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {"message": "Utilisateur inexistant"},
                    status.HTTP_404_NOT_FOUND
                )
        if serializer.is_valid():
            number = Role.objects.all().filter(
                ~Q(id=kwargs['pk']),
                name=serializer.validated_data['name'],
                restaurant=restaurant,
                is_deleted=False
            ).count()
            if number >= 1:
                logger.error(
                    "Un role existe avec ce nom",
                    extra={
                        'restaurant': restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Un role existe avec ce nom"},
                    status=status.HTTP_409_CONFLICT)

            role = self.perform_update(serializer)
            users = get_user_model().objects.all().filter(
                roles=role,
                restaurant=restaurant,
                is_deleted=False
            )
            for user in users:
                user.roles.remove(role)
            for user in users_add:
                user.roles.add(role)
                user.save()

            data = {
                "id": serializer.data['id'],
                "name": serializer.data['name'],
                "permissions": serializer.data['permissions'],
                "is_active": serializer.data['is_active'],
                "description": serializer.data['description'],
                "reference": serializer.data['reference'],
                "users": UserSerializer(users_add, many=True).data
            }
            logger.info(
                "role modifié avec succès",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(data)
        else:
            logger.error(
                str(serializer.errors),
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                serializer.errors,
                status=status.HTTP_412_PRECONDITION_FAILED)

    def perform_update(self, serializer):
        """Docstring for function."""
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        if request.user.is_staff is False:
            logger.error(
                "Vous n'avez pas accès à la suppression",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Vous n'avez pas les droits nécessaires"},
                status.HTTP_403_FORBIDDEN)
        connection.set_schema_to_public()
        try:
            role = Role.objects.get(
                pk=kwargs['pk'],
                is_deleted=False
            )
        except Role.DoesNotExist:
            logger.error(
                "Role inexistant!",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {"message": "Rôle inexistant"},
                status.HTTP_404_NOT_FOUND
            )

        users = get_user_model().objects.all().filter(
            roles=role,
            is_deleted=False
        ).count()

        if users >= 1:
            logger.error(
                "Des utilisateurs sont liés à ce role",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {'message': "Des utilisateurs sont liés à ce role"},
                status=status.HTTP_409_CONFLICT)

        self.perform_destroy(role)
        logger.info(
            "Role supprimé avec succès",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
