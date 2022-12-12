import logging
from datetime import datetime, timezone
from uuid import uuid4
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant_from_restaurant, set_tenant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantCommande.models.note import Note
from restaurantCommande.models.note import NoteComments
from accounts.models.restaurant import Restaurant
from django.template.loader import render_to_string
from core.utils import send_mail
from notifications.notifications_message import send_sms_message
from restaurantCommande.models.commande import Commande
from threading import Thread
from restaurantCommande.check_distance_delivery import check_distance_delivery
from restaurantCommande.serializers.validate_commande import ValidateCommandeSerializer, ValidateCommandeCreateSerializer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from core.schemas.schema_commande import schema_response_commande
from restaurantCommande.utils import *

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

restaurant_param = openapi.Parameter('restaurant', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER, required=True)

correct_response = openapi.Response(
    description='Vérification de la commande par le livreur',
    schema=schema_response_commande,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')


@swagger_auto_schema(method='put',
                     request_body=ValidateCommandeCreateSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response})
@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def delivery_check_commande(request, commande):
    """Docstring for function."""
    user = request.user
    if user.delivery is None:
        logger.error(
            {'message': "Vous n'avez pas accès pour checker une commande"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès pour checker une commande"},
            status.HTTP_403_FORBIDDEN)
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
    serializer = ValidateCommandeSerializer(data=request.data)
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

    # Verifier si la commande a été validée par le livreur et par le restaurant
    if (instance.is_delivery_valid is None or
            instance.is_delivery_valid is False or
            instance.is_restaurant_valid is None or
            instance.is_restaurant_valid is False):
        logger.error(
            "Il faut faire valider la commande par le restaurant et par un livreur",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Il faut faire valider la commande par le restaurant et par un livreur"},
            status=status.HTTP_409_CONFLICT)

    # Verifier si l'utilisateur qui check est égal à l'utilisateur qui a validé la livraison
    if instance.delivery_validated_by != user:
        logger.error(
            "Vous ne pouvez pas checker une commande que vous n'avez pas validé",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous ne pouvez pas checker une commande que vous n'avez pas validé"},
            status=status.HTTP_409_CONFLICT)
    mes = None
    if serializer.validated_data['valid_status'] is True:
        if instance.is_delivery_check is True:
            logger.error(
                "Cette commande est deja checké",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Cette commande est déjà checké"},
                status=status.HTTP_409_CONFLICT)

        instance.delivery_check_date = datetime.now()
        instance.token = uuid4().hex[:5].upper()
        instance.status = 4
        message = 'La commande a été checké avec succès'
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
        if instance.is_delivery_valid is not None and instance.is_delivery_valid is True:
            diff = datetime.now(timezone.utc) - instance.delivery_validate_date
            if int(diff.total_seconds()) > settings.MAX_TIME['cancel_valid_commande']*60:
                logger.error(
                    "Vous ne pouvez plus annuler le check de cette commande car le temps possible d'annulation est terminé",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Vous ne pouvez plus annuler le check de cette commande car le temps possible d'annulation est terminé"},
                    status=status.HTTP_409_CONFLICT)

        instance.delivery_check_date = datetime.now()
        instance.status = 3
        message = "L'annulation du check de la commande a été faite avec succès"

    instance.is_delivery_check = serializer.validated_data['valid_status']
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

    # on notifie le client si la commande est checkée par le livreur également
    if instance.is_delivery_check is True:
        message_sms = "Hello! C'est WaziEats, \nVotre commande est en cours de livraison.\n Informations du livreur\n\t NOM: " + \
                      user.last_name + "\n\t PRENOM: " + user.first_name + "\n\nMerci de nous faire confiance."
        send_sms_message(request, instance.created_by, message_sms)

        if instance.created_by.restaurant is None and instance.created_by.is_client is None and instance.created_by.delivery is None:
            login_url = settings.APP['admin_url'] + 'login'
        else:
            login_url = settings.APP['site_url'] + 'login'

        context = {
            'email': instance.created_by,
            'login_url': login_url,
            'site_name': settings.APP['site_name'],
            'nom': user.last_name,
            'prenom': user.first_name,
            'en_tete': 'Livraison de la commande'
        }

        subject = 'Livraison de la commande'

        html_content = render_to_string(
            'email/accounts/infos_delivery.html',
            context
        )
        text_content = render_to_string(
            'email/accounts/infos_delivery.txt',
            context
        )

        send_mail(request, instance.created_by.email, subject, text_content, html_content)

        t1 = Thread(
            target=check_distance_delivery,
            args=(request, commande, instance.created_by)
        )
        t1.start()

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
