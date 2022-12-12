import logging
from uuid import uuid4
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from core.pagination import CustomPageNumberPagination
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from core.utils import send_mail
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from accounts.serializers.change_password import ChangePasswordSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

logger = logging.getLogger("myLogger")

correct_response = openapi.Response('Message de confirmation de la modification')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


class ChangePasswordView(generics.UpdateAPIView):
    """Docstring for class."""

    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    http_method_names = ['put']

    @swagger_auto_schema(responses={200: correct_response, 400: bad_request, 412: error_response})
    def put(self, request):
        """Docstring for function."""
        connection.set_schema_to_public()
        user = request.user
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                if not user.check_password(serializer.validated_data['old_password']):
                    logger.error(
                        "Mot de passe incorrect",
                        extra={
                            'restaurant': request.user.restaurant,
                            'user': request.user.id
                        }
                    )
                    return Response(
                        {
                            "message": "Mot de passe incorrect"
                        },
                        status.HTTP_400_BAD_REQUEST
                    )

                new_password = serializer.validated_data['new_password']
                confirm_password = serializer.validated_data['confirm_password']

                if new_password != confirm_password:
                    logger.error(
                        "Le mot de passe et sa confirmation sont différents",
                        extra={
                            'restaurant': request.user.restaurant,
                            'user': request.user.id
                        }
                    )
                    return Response(
                        {
                            "message": "Le mot de passe et sa confirmation sont différents"
                        },
                        status.HTTP_400_BAD_REQUEST
                    )

                user.set_password(new_password)
                user.password_requested_at = None
                user.save()

                logger.info(
                    "Mot de passe modifié avec succès",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {"message": "Mot de passe modifié avec succès"},
                    status=status.HTTP_200_OK
                )
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
