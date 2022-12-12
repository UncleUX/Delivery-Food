import logging
from uuid import uuid4
import datetime
import requests
import json
from rest_framework.response import Response
from rest_framework.views import APIView
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
from accounts.serializers.forget_password import ForgotPasswordSerializer
from accounts.models.restaurant import Restaurant, Domain
from accounts.models.user import User
from rest_framework import generics
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response('Message de confirmation')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


class ForgotPassword(generics.CreateAPIView):
    """Docstring for class."""

    serializer_class = ForgotPasswordSerializer
    http_method_names = ['post']

    @swagger_auto_schema(responses={200: correct_response, 400: bad_request, 412: error_response})
    def post(self, request):
        """Docstring for function."""
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                env = serializer.validated_data['env']
                user = None
                if env.lower() == 'user':
                    try:
                        user = get_user_model().objects.get(
                            is_client=False,
                            delivery__isnull=True,
                            phone=serializer.validated_data['phone']
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
                            phone=serializer.validated_data['phone']
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
                            phone=serializer.validated_data['phone']
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
                            phone=serializer.validated_data['phone']
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

                reset_token = uuid4()
                user.reset_token = reset_token
                user.password_requested_at = datetime.datetime.now()
                user.save()
                if env == 'admin':
                    url = settings.APP['admin_url'] + '/reset-password?token='
                    site_url = settings.APP['admin_url']
                    login_url = settings.APP['admin_url'] + '/login'
                else:
                    url = settings.APP['site_url'] + '/reset-password?token='
                    site_url = settings.APP['site_url']
                    login_url = settings.APP['site_url'] + '/login'

                url = url + str(reset_token) + '&phone=' + str(user.phone)

                context = {
                    'site_name': settings.APP['site_name'],
                    'site_url': site_url,
                    'url': url,
                    'login_url': login_url,
                    'phone': user.phone
                }

                subject = 'Mot de passe oublié'

                html_content = render_to_string(
                    'email/accounts/forget_password.html',
                    context
                )
                text_content = None
                """
                text_content = render_to_string(
                    'email/accounts/forget_password.txt',
                    context
                )
                """
                # send SMS
                access_token = None
                token_type = None
                url = "https://api.orange.com/oauth/v3/token"
                body = {
                    "grant_type": "client_credentials"
                }
                headers = {'Authorization': 'Basic ODNmOEdvSWF5c3lVOWR0UHFzS1p0b2IxTlVjOUdwS1c6WHFFM050dWozTUJlMnA3VA=='}
                r = requests.post(url, data=json.dumps(body), headers=headers)
                if r.status_code == 200 or r.status_code == 201:
                    res = r.json()
                    access_token = res['access_token']
                    token_type = res['token_type']
                else:
                    logger.info(
                        "Impossible de récupérer les credentials.",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )

                if access_token is None:
                    access_token = settings.ACCESS_TOKEN
                    token_type = settings.TYPE_TOKEN

                devPhoneNumber = settings.WAZIEATS_PHONE_NUMBER

                message = "Hello! C'est WaziEats, \nCliquez sur ce lien pour modifier votre mot de passe " + url \
                          + "\nSi vous n'avez pas fait cette demande, veuillez ignorer ce message."

                url = "https://api.orange.com/smsmessaging/v1/outbound/tel%3A%2B" + str(devPhoneNumber)[1:] + "/requests"
                body = {
                    "outboundSMSMessageRequest": {
                        "address": "tel:" + str(user.phone),
                        "senderAddress": "tel:" + str(devPhoneNumber),
                        "outboundSMSTextMessage": {
                            "message": message
                        }
                    }
                }
                headers = {
                    'Authorization': str(token_type) + ' ' + str(access_token),
                    'Content-Type': "application/json",
                    'Host': "api.orange.com"
                }
                r = requests.post(url, data=json.dumps(body), headers=headers)
                if r.status_code == 200 or r.status_code == 201:
                    logger.info(
                        "SMS envoyé avec succès.",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                else:
                    logger.info(
                        "Impossible d'envoyer de SMS.",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                send_mail(request, user.email, subject, text_content, html_content)

                logger.info(
                    "Demande réussie!",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response({"message": "Demande prise en compte"})

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
