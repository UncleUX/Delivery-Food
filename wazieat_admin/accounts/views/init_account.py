import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models.user import User
from django.conf import settings
from django.db import connection
from notifications.notifications_message import notifications_message
from notifications.notifications_admin import notifications_admin
from notifications.notifications_confirm_initAccount_delivery import notifications
from django.template.loader import render_to_string
from accounts.serializers.init_account import InitAccountSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

logger = logging.getLogger("myLogger")

correct_response = openapi.Response('Message de confirmation')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


class InitAccount(generics.CreateAPIView):
    """Docstring for class."""

    serializer_class = InitAccountSerializer
    http_method_names = ['post']

    @swagger_auto_schema(responses={200: correct_response, 400: bad_request, 412: error_response})
    def post(self, request):
        """Docstring for function."""
        connection.set_schema_to_public()
        try:
            serializer = InitAccountSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                try:
                    user = get_user_model().objects.get(
                        reset_token=serializer.validated_data['token'],
                        phone=serializer.validated_data['phone'],
                        is_active=False,
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

                if not user.requested_token_valid():
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
                user.save()
                if user.delivery is not None:
                    message_sms = "Hello! C'est WaziEats, \nVotre compte a été initialisé avec succès. Vous allez recevoir un mot de passe pour vous connecter dans un delay de 24 heures.\nMerci de votre confiance."
                    notifications(request, user, message_sms)
                    admin = User.objects.get(is_active=True, is_deleted=False, is_admin=True, is_staff=True)
                    name = user.last_name
                    if user.first_name is not None and user.first_name != '':
                        name = name + " " + str(user.first_name)
                    notifications_admin(request, admin, "livreur", name, user.email)
                else:
                    subject = 'Confirmation du compte'
                    message_sms = "Hello! C'est WaziEats, \nVotre compte a été activée.\nMerci de nous faire confiance."
                    message_mail = "Votre compte a été activée."
                    en_tete = 'Confirmation de validation du compte'
                    flag = 0
                    notifications_message(request, user, subject, message_sms, message_mail, en_tete, flag)
                logger.info(
                    "Compte initialisé avec succès.",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {
                        "message": "Compte initialisé avec succès."
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
