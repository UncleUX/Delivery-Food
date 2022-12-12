import json
import logging
from datetime import datetime, timezone
from uuid import uuid4
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from accounts.models.user import User
from django.db import connection
from threading import Thread
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from accounts.models.restaurant import Restaurant
from restaurantCommande.models.commande import Commande
from notifications.notif_cancel_commande import notif_cancel_suggest_commande
from notifications.notif_cancel_commande import notif_cancel_commande
from restaurantCommande.serializers.suggestion_commande import SuggestionResponseCommandeSerializer
from core.schemas.schema_commande import schema_response_commande
from notifications.notifications_message import notifications_message
from restaurantCommande.utils import *

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Suggestion d\'une commande',
    schema=schema_response_commande,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='put',
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def suggestion_response_commande(request):
    """Docstring for function."""
    user = request.user
    if user.is_client is False:
        logger.warning(
            "Vous n'avez pas accès à la suggestion des commandes",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la suggestion des commandes"},
            status=status.HTTP_403_FORBIDDEN)
    connection.set_schema_to_public()
    # Gestion des tenants en fonction des utilisateurs
    try:
        restaurant = Restaurant.objects.get(pk=request.data['restaurant'], is_active=True)
    except Restaurant.DoesNotExist:
        logger.warning(
            "Un restaurant avec cette cle primaire n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Un restaurant avec cette cle primaire n'existe pas"},
            status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        logger.warning(
            "Le champ restaurant est absent dans la requête",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Le champ restaurant est absent dans la requête"},
            status=status.HTTP_400_BAD_REQUEST)
    set_tenant_from_restaurant(restaurant)
    serializer = SuggestionResponseCommandeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    commande = serializer.validated_data['commande']
    if commande.suggestion is None:
        logger.warning(
            "Cette commande n'a pas de suggestion",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Cette commande n'a pas de suggestion"},
            status=status.HTTP_400_BAD_REQUEST)
    if serializer.validated_data['response'] is False:
        commande.is_active = False
        commande.is_deleted = True
        commande.save()
        subject = 'Annulation de la commande'
        message_sms = "Hello! C'est WaziEats, \nL'annulation de votre commande " + str(commande.reference) + " a été prise en compte avec succès.\nMerci de nous faire confiance."
        message_mail = "L'annulation de votre commande " + str(commande.reference) + " a été prise en compte avec succès.\nMerci de nous faire confiance."
        en_tete = 'Annulation de la commande'
        flag = 1
        notifications_message(request, commande.created_by, subject, message_sms, message_mail, en_tete, flag)
        subject = 'Annulation de la commande'
        message_sms = "Hello! C'est WaziEats, \nMalheureusement, le client a rejeté la suggestion de la commande " + str(commande.reference) + ". Nous devons l'annuler.\nMerci de nous faire confiance."
        message_mail = "Malheureusement, le client a rejeté la suggestion de la commande " + str(commande.reference) + ". Nous devons l'annuler.\nMerci de nous faire confiance."
        en_tete = 'Annulation de la commande'
        flag = 0
        notifications_message(request, commande.restaurant_suggest_by, subject, message_sms, message_mail, en_tete, flag)
    else:
        commande.is_restaurant_valid = serializer.validated_data['response']
        commande.restaurant_validated_by = commande.restaurant_suggest_by
        commande.restaurant_validate_date = datetime.now()
        commande.status = 3
        commande.save()
        subject = 'Acceptation de la suggestion de la commande'
        message_sms = "Hello! C'est WaziEats, \n Le client a validé la suggestion de la commande " + str(commande.reference) + ". Vous pouvez commencer la préparation.\nMerci de nous faire confiance."
        message_mail = "Malheureusement, le client a rejeté la suggestion de la commande " + str(commande.reference) + ". Vous pouvez commencer la préparation.\nMerci de nous faire confiance."
        en_tete = 'Acceptation de la suggestion de la commande'
        flag = 0
        notifications_message(request, commande.restaurant_suggest_by, subject, message_sms, message_mail, en_tete, flag)
        # Notification Client si commande non validée
        t3 = Thread(
            target=notif_cancel_commande,
            args=(request, commande, user, restaurant)
        )
        t1.start()

    logger.info(
        "Réponse prise en compte avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        {'message': "Réponse prise en compte avec succès"},
        status.HTTP_200_OK)

