import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response('Message de confirmation de déconnexion')


class Logout(APIView):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: correct_response})
    def get(self, request):
        """Docstring for function."""
        request.user.auth_token.delete()
        logger.info(
            "Déconnexion réussie",
            extra={
                'restaurant': request.user.restaurant,
                'user': request.user.id
            }
        )
        return Response({'message': "Déconnexion réussie"}, status=status.HTTP_200_OK)
