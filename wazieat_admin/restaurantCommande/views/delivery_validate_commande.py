import logging
from datetime import datetime, timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantCommande.models.note import Note
from restaurantCommande.models.note import NoteComments
from threading import Thread
from restaurantCommande.models.commande import Commande
from restaurantCommande.serializers.validate_commande import ValidateCommandeSerializer, ValidateCommandeCreateSerializer
from restaurantCommande.views.commande import thread_send_notif_delivery
from notifications.notifications_message import notifications_message
from core.schemas.schema_commande import schema_response_commande
from accounts.models.restaurant import Restaurant
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from restaurantCommande.utils import *

logger = logging.getLogger("myLogger")

restaurant_param = openapi.Parameter('restaurant', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER, required=True)

correct_response = openapi.Response(
    description='Validation/Rejet de la commande par le livreur',
    schema=schema_response_commande,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='put',
                     request_body=ValidateCommandeCreateSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def delivery_validate_commande(request, commande):
    """Docstring for function."""
    user = request.user
    if user.delivery is None:
        logger.error(
            {'message': "Vous n'avez pas accès à la validation d'une commande"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la validation d'une commande"},
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

    try:
        mes = None
        set_tenant_from_restaurant(restaurant)
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
        serializer = ValidateCommandeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['valid_status'] is True:
            if instance.is_delivery_valid is not None and instance.is_delivery_valid is True:
                logger.error(
                    "Cette commande est deja validée pour livraison",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Cette commande est deja validée pour livraison"},
                    status=status.HTTP_409_CONFLICT)
            instance.delivery_validated_by = user
            instance.delivery_validate_date = datetime.now()
            if instance.is_restaurant_valid is None or instance.is_restaurant_valid is not True:
                instance.status = 2
            message = "La commande a été validé avec succès"
            try:
                mes = serializer.validated_data['message']
            except KeyError:
                pass
        else:
            try:
                mes = serializer.validated_data['message']
            except KeyError:
                logger.error(
                    "Vous devez donner la raison du rejet de la commande",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Vous devez donner la raison du rejet de la commande"},
                    status=status.HTTP_400_BAD_REQUEST)
            if instance.is_delivery_valid is None:
                logger.error(
                    "Vous ne pouvez pas annuler une commande qui n'est pas validé",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Vous ne pouvez pas annuler une commande qui n'est pas validé"},
                    status=status.HTTP_400_BAD_REQUEST)
            if instance.is_delivery_valid is not None and instance.is_delivery_valid is True:
                if instance.delivery_validated_by != request.user:
                    logger.error(
                        "Vous ne pouvez plus annuler une commande que vous n'avez pas validé",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {'message': "Vous ne pouvez plus annuler une commande que vous n'avez pas validé"},
                        status=status.HTTP_409_CONFLICT)
                diff = datetime.now(timezone.utc) - instance.delivery_validate_date
                if int(diff.total_seconds()) > settings.MAX_TIME['cancel_valid_commande']*60:
                    logger.error(
                        "Vous ne pouvez plus annuler cette commande car le temps possible d'annulation est terminé",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {'message': "Vous ne pouvez plus annuler cette commande car le temps possible d'annulation est terminé"},
                        status=status.HTTP_409_CONFLICT)
            instance.delivery_cancel_validated_by = user
            instance.delivery_cancel_date = datetime.now()
            if instance.is_restaurant_valid is None or instance.is_restaurant_valid is not True:
                instance.status = 1
            message = "L'annulation de la validation de la commande a été faite avec succès"
        instance.is_delivery_valid = serializer.validated_data['valid_status']
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

        # on notifie le client si la commande est validé par le livreur également
        if instance.is_delivery_valid is True and instance.is_restaurant_valid is True:
            subject = 'Validation de la commande'
            message_sms = "Hello! C'est WaziEats, \nVotre commande est validée et est en cours de traitement.\nMerci de nous faire confiance."
            message_mail = "Votre commande est validée et est en cours de traitement."
            en_tete = 'Validation de la commande'
            flag = 1
            t1 = Thread(
                target=notifications_message,
                args=(request, instance.created_by, subject, message_sms, message_mail, en_tete, flag)
            )
            t1.start()

        # On notifie les autres livreurs si annulation de la validation
        if instance.is_delivery_valid is False :
            subject = 'Commande pour livraison'
            message_sms = "Hello! C'est WaziEats, \nVous avez une commande non validée.\nMerci de nous faire confiance."
            message_mail = "Vous avez une commande non validée."
            en_tete = 'Commande pour livraison'
            flag = 1
            t2 = Thread(
                target=thread_send_notif_delivery,
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
    except Commande.DoesNotExist:
        logger.warning(
            "Cette commande n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Cette commande n'existe pas"},
            status=status.HTTP_400_BAD_REQUEST)

