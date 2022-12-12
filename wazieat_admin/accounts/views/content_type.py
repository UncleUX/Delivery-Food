import logging
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connection

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")


schema_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant", type=openapi.TYPE_INTEGER,),
        "app_label": openapi.Schema(title="app_label", description="Application du modèle", type=openapi.TYPE_STRING,),
        "model": openapi.Schema(title="model", description="Modèle de la BD", type=openapi.TYPE_STRING,),
    }
)

correct_response = openapi.Response(description='Création/Modification/Visualisation d\'une commande', schema=schema_response,)
forbidden_request = openapi.Response('Pas de permissions')


class ContentView(APIView):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    @staticmethod
    @swagger_auto_schema(
        responses={403: forbidden_request, 200: correct_response})
    def get(request):
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

        connection.set_schema_to_public()
        contents = []
        datas = ContentType.objects.all()
        for content in datas:
            contents.append({
                'id': content.id,
                'app_label': content.name,
                'model': content.model
            })

        logger.info(
            "Liste des fonctionnalités renvoyés avec succès",
            extra={
                'restaurant': None,
                'user': request.user.id
            }
        )
        return Response(contents)
