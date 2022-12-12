import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

schema_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant", type=openapi.TYPE_INTEGER,),
        "name": openapi.Schema(title="name", description="Nom de la permission", type=openapi.TYPE_STRING,),
    }
)

correct_response = openapi.Response(description='Liste des permissions', schema=schema_response,)
forbidden_request = openapi.Response('Pas de permissions')


class Permissions(APIView):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]
    serializer_class = None

    @swagger_auto_schema(responses={403: forbidden_request, 200: correct_response})
    def get(self, request):
        """Docstring for function."""

        if request.user.is_staff is False:
            logger.error(
                "Vous n'avez pas accès à la liste des restaurants",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
            return Response(
                {
                    "message": "Vous n'avez pas les droits nécessaires",
                }, status.HTTP_403_FORBIDDEN)

        restaurant = request.user.restaurant
        permissions = []
        if restaurant:
            if restaurant.module:
                for mod in restaurant.module.all():
                    for contenttype in mod.contenttypes.all():
                        perms = Permission.objects.all().filter(
                            content_type=contenttype)
                        for perm in perms:
                            permissions.append({
                                "id": perm.id,
                                "name": perm.name
                            })

            logger.info(
                "Permissions renvoyées avec succès",
                extra={
                    'restaurant': None,
                    'user': request.user.id
                }
            )
        else:
            datas = Permission.objects.all()
            for permission in datas:
                permissions.append({
                    'id': permission.id,
                    'name': permission.name
                })

            logger.info(
                "Permissions renvoyées avec succès",
                extra={
                    'restaurant': None,
                    'user': request.user.id
                }
            )
        return Response(permissions)
