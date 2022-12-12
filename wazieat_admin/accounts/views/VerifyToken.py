import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.serializers.verify_token import VerifyTokenSerializer
from accounts.models.user import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

logger = logging.getLogger("myLogger")

correct_response = openapi.Response('Message de confirmation')
bad_request = openapi.Response('Message de mauvaise requête')
not_found = openapi.Response('Message d\'utilisateur inexistant')
error_response = openapi.Response('Message de token expiré')


class VerifyToken(generics.CreateAPIView):
    """Docstring for class."""

    serializer_class = VerifyTokenSerializer
    http_method_names = ['post']

    @swagger_auto_schema(responses={200: correct_response, 400: bad_request, 404: not_found, 408: error_response})
    def post(self, request):
        """Docstring for function."""
        try:
            serializer = VerifyTokenSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = None
                env = serializer.validated_data['env']
                if env.lower() == 'user':
                    try:
                        user = get_user_model().objects.get(
                            is_client=False,
                            delivery__isnull=True,
                            reset_token=serializer.validated_data['token']
                        )
                    except User.DoesNotExist:
                        logger.error(
                            "Utilisateur inexistant",
                            extra={
                                'restaurant': None,
                                'user': None
                            }
                        )
                        return Response(
                            {
                                "message": "Utilisateur inexistant"
                            },
                            status.HTTP_404_NOT_FOUND)
                elif env.lower() == 'livreur':
                    try:
                        user = get_user_model().objects.get(
                            restaurant=None,
                            is_client=False,
                            delivery__isnull=False,
                            reset_token=serializer.validated_data['token']
                        )
                    except User.DoesNotExist:
                        logger.error(
                            "Utilisateur inexistant",
                            extra={
                                'restaurant': None,
                                'user': None
                            }
                        )
                        return Response(
                            {
                                "message": "Utilisateur inexistant"
                            },
                            status.HTTP_404_NOT_FOUND)
                elif env.lower() == 'client':
                    try:
                        user = get_user_model().objects.get(
                            restaurant=None,
                            is_client=True,
                            delivery__isnull=True,
                            reset_token=serializer.validated_data['token']
                        )
                    except User.DoesNotExist:
                        logger.error(
                            "Utilisateur inexistant",
                            extra={
                                'restaurant': None,
                                'user': None
                            }
                        )
                        return Response(
                            {
                                "message": "Utilisateur inexistant"
                            },
                            status.HTTP_404_NOT_FOUND)
                elif env.lower() == 'admin':
                    try:
                        user = get_user_model().objects.get(
                            restaurant=None,
                            is_client=False,
                            delivery__isnull=True,
                            reset_token=serializer.validated_data['token']
                        )
                    except User.DoesNotExist:
                        logger.error(
                            "Cet utilisateur n'est pas un superadmin",
                            extra={
                                'restaurant': None,
                                'user': None
                            }
                        )
                        return Response(
                            {
                                "message": "Cet utilisateur n'est pas un superadmin"
                            },
                            status.HTTP_404_NOT_FOUND
                        )

                if user.requested_token_valid() is True:
                    logger.info(
                        "Token valide!",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {"message": "Token valide"},
                        status.HTTP_200_OK
                    )
                else:
                    logger.error(
                        "Token invalide!",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {"message": "Token expiré"},
                        status.HTTP_408_REQUEST_TIMEOUT
                    )

        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': None,
                    'user': None
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)
