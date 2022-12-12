import logging
import datetime
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantCommande.models.note import Note
from accounts.models.restaurant import Restaurant
from restaurantCommande.models.commande import Commande
from restaurantCommande.models.note import NoteComments
from threading import Thread
from restaurantCommande.views.commande import thread_send_notif_restau
from notifications.notifications_message import notifications_message
from restaurantCommande.serializers.livraison_commande import LivraisonCommandeSerializer, LivraisonCreateCommandeSerializer
from core.schemas.schema_commande import schema_response_commande
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from restaurantCommande.utils import *


logger = logging.getLogger("myLogger")

restaurant_param = openapi.Parameter('restaurant', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER, required=True)

correct_response = openapi.Response(
    description='Livraison de la commande par le livreur',
    schema=schema_response_commande,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='put',
                     request_body=LivraisonCreateCommandeSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def livraison_commande(request, commande):
    """Docstring for function."""
    user = request.user
    if user.delivery is None:
        logger.error(
            {'message': "Vous n'avez pas accès pour faire une livraison"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès pour faire une livraison"},
            status.HTTP_403_FORBIDDEN)

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
    serializer = LivraisonCommandeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        instance = Commande.objects.get(pk=commande, is_active=True, is_deleted=False)
    except Commande.DoesNotExist:
        logger.warning(
            "Une commande avec cette clé primaire n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Une commande avec cette clé primaire n'existe pas"},
            status=status.HTTP_400_BAD_REQUEST)

    # Verifier si la commande a été checkée par un livreur
    if instance.is_delivery_check is None or instance.is_delivery_check is False:
        logger.error(
            "Cette commande ne peut être livrée car elle n'a pas encore été checkée",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Cette commande ne peut être livrée car elle n'a pas encore été checkée"},
            status=status.HTTP_409_CONFLICT)

    # Verifier si la commande n'a pas été livrée
    if instance.status == 5:
        logger.error(
            "Cette commande est deja livrée",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Cette commande est deja livrée"},
            status=status.HTTP_409_CONFLICT)

    if instance.token != serializer.validated_data['code']:
        logger.error(
            "Le code de cette commande est incorrect",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Le code de cette commande est incorrect"},
            status=status.HTTP_400_BAD_REQUEST)
    mes = None
    try:
        mes = serializer.validated_data['message']
    except KeyError:
        pass
    instance.delivery_date = datetime.now()
    instance.status = 5
    message = 'La commande a été checké avec succès'
    instance.is_delivery_check = True
    if mes is not None:
        com = NoteComments()
        com.comment = mes
        com.save()
        note = Note()
        note.comments = com
        note.commande = instance
        note.created_by = user
        note.save()

    instance.save()
    note = Note.objects.all().filter(commande=instance).order_by('-id')
    result = get_commande(instance, note, restaurant)

    # Same price
    result['food_same_price'] = get_food_same_price(instance)
    result['drink_same_price'] = get_drink_same_price(instance)

    # on notifie le client
    subject = 'Livraison de la commande effectuée'
    message_sms = "Hello! C'est WaziEats, \nVotre commande vient d'être effectuée avec succès.\nMerci de nous faire confiance."
    message_mail = "Votre commande vient d'être effectuée avec succès."
    en_tete = 'Livraison de la commande effectuée'
    flag = 1
    t1 = Thread(
        target=notifications_message,
        args=(request, instance.created_by, subject, message_sms, message_mail, en_tete, flag)
    )
    t1.start()

    # notifications de tous les utilisateurs du restaurant
    t2 = Thread(
        target=thread_send_notif_restau,
        args=(request, subject, message_sms, message_mail, en_tete, flag, restaurant)
    )
    t2.start()

    logger.info(
        message,
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        result,
        status.HTTP_200_OK)

