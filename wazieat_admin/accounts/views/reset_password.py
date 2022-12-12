import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models.user import User
from core.utils import send_mail
from django.conf import settings
from notifications.notifications_message import notifications_message
from django.template.loader import render_to_string
from accounts.serializers.change_password import ResetPasswordSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

logger = logging.getLogger("myLogger")

correct_response = openapi.Response('Message de confirmation')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


class ResetPassword(generics.CreateAPIView):
    """Docstring for class."""

    serializer_class = ResetPasswordSerializer
    http_method_names = ['post']

    @swagger_auto_schema(responses={200: correct_response, 400: bad_request, 412: error_response})
    def post(self, request):
        """Docstring for function."""
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
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
                try:
                    user = get_user_model().objects.get(
                        reset_token=serializer.validated_data['token'],
                        is_active=True,
                        is_deleted=False
                    )
                except User.DoesNotExist:
                    logger.error(
                        "Utilisateur inexistant!",
                        extra={
                            'restaurant': None,
                            'user': None
                        }
                    )
                    return Response(
                        {
                            "message": "Utilisateur inexistant"
                        },
                        status.HTTP_404_NOT_FOUND
                    )

                if user.requested_token_valid() is False:
                    logger.error(
                        "Token expiré",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {"message": "Token expiré"},
                        status.HTTP_408_REQUEST_TIMEOUT
                    )

                user.password_requested_at = None
                user.reset_token = None
                user.set_password(new_password)
                user.save()
                subject = 'Confirmation du compte'
                message_sms = "Hello! C'est WaziEats, \nVotre mot de passe a été modifiée.\nMerci de nous faire confiance."
                message_mail = "Votre mot de passe a été modifiée."
                en_tete = 'Confirmation de modification du mot de passe'
                flag = 0
                notifications_message(request, user, subject, message_sms, message_mail, en_tete, flag)
                logger.info(
                    "Mot de passe modifié avec succès.",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {
                        "message": "Mot de passe modifié avec succès."
                    }
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
