import logging
import datetime
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant_from_restaurant, set_tenant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantCommande.serializers.note import NoteSerializer, NoteCreateSerializer, NoteCommentsSerializer
from restaurantCommande.models.note import Note
from restaurantCommande.serializers.commande import CommandeSerializer
from restaurantCommande.views.commande import thread_send_notif_restau
from accounts.serializers.user import UserSerializer
from accounts.models.restaurant import Restaurant
from restaurantCommande.models.commande import Commande
from core.schemas.schema_notes import schema_response_note, schema_response_note_list
from threading import Thread
from notifications.notifications_message import notifications_message
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from drf_yasg import openapi
from restaurantCommande.utils import *
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

restaurant_param = openapi.Parameter('restaurant', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER, required=True)
page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER)
size_param = openapi.Parameter('size', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER)

correct_response = openapi.Response(
    description='Création de la note',
    schema=schema_response_note,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


@swagger_auto_schema(method='post',
                     request_body=NoteCreateSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response, 412: error_response})
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def create_note(request):
    """Docstring for function."""
    user = request.user
    if user.has_perm('restaurantCommande.add_note') is False and user.is_client is False:
        logger.error(
            {'message': "Vous n'avez pas accès à la création d'une note"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la création d'une note"},
            status.HTTP_403_FORBIDDEN)
    restaurant = None
    # Gestion des tenants en fonction des utilisateurs
    if user.is_client is True:
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
                "Le champ restaurant est absent dans la requete",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Le champ restaurant est absent dans la requete"},
                status=status.HTTP_400_BAD_REQUEST)
        set_tenant_from_restaurant(restaurant)
    else:
        set_tenant(request)

    serializer = NoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if check_foods(serializer) is False:
        logger.warning(
            "Vous commentez un plat qui ne se trouve pas dans votre commande",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous commentez un plat qui ne se trouve pas dans votre commande"},
            status=status.HTTP_400_BAD_REQUEST)
    if check_drinks(serializer) is False:
        logger.warning(
            "Vous commentez une boisson qui ne se trouve pas dans votre commande",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous commentez une boisson qui ne se trouve pas dans votre commande"},
            status=status.HTTP_400_BAD_REQUEST)
    note = serializer.save(created_by=user)
    result = {
        'id': note.id,
        'reference': note.reference,
        'comments': NoteCommentsSerializer(note.comments).data,
        'created_by': UserSerializer(note.created_by).data,
        'commande': CommandeSerializer(note.commande).data,
        'created_at': note.created_at,
        'updated_at': note.updated_at
    }
    # Notification du client ou tous les utilisateurs du restaurant
    subject = 'Nouvelle note sur la commande ' + note.commande.reference
    message_sms = "Hello! C'est WaziEats, \nVous avez reçu une note sur la commande " + note.commande.reference + ".\nMerci de nous faire confiance."
    message_mail = "Vous avez reçu une note sur la commande " + note.commande.reference
    en_tete = 'Nouvelle note de la commande'
    flag = 0
    if user.is_client is True:
        t1 = Thread(
            target=thread_send_notif_restau,
            args=(request, subject, message_sms, message_mail, en_tete, flag, restaurant)
        )
        t1.start()
    else:
        t1 = Thread(
            target=notifications_message,
            args=(request, note.commande.created_by, subject, message_sms, message_mail, en_tete, flag)
        )
        t1.start()

    logger.info(
        "Le commentaire a été crée avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        result,
        status.HTTP_201_CREATED)


correct_response_change = openapi.Response(
    description='Modification de la note',
    schema=schema_response_note,)


@swagger_auto_schema(method='put',
                     request_body=NoteCreateSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response_change, 412: error_response})
@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def change_note(request, note):
    """Docstring for function."""
    user = request.user
    if user.has_perm('restaurantCommande.change_note') is False and user.is_client is False:
        logger.error(
            {'message': "Vous n'avez pas accès à la modification d'une note"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la modification d'une note"},
            status.HTTP_403_FORBIDDEN)
    restaurant = None
    # Gestion des tenants en fonction des utilisateurs
    if user.is_client is True:
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
                "Le champ restaurant est absent dans la requete",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Le champ restaurant est absent dans la requete"},
                status=status.HTTP_400_BAD_REQUEST)
        set_tenant_from_restaurant(restaurant)
    else:
        set_tenant(request)
    try:
        instance = Note.objects.get(pk=note)
        serializer = NoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if instance.commande != serializer.validated_data['commande']:
            logger.info(
                "Cette note appartient a une autre commande",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Cette note appartient a une autre commande"},
                status=status.HTTP_400_BAD_REQUEST)
        if user != instance.created_by:
            logger.info(
                "Impossible de modifier la note d'un autre client",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Impossible de modifier la note d'un autre client"},
                status=status.HTTP_400_BAD_REQUEST)
        if check_foods(serializer) is False:
            logger.warning(
                "Vous commentez un plat qui ne se trouve pas dans votre commande",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous commentez un plat qui ne se trouve pas dans votre commande"},
                status=status.HTTP_400_BAD_REQUEST)
        if check_drinks(serializer) is False:
            logger.warning(
                "Vous commentez une boisson qui ne se trouve pas dans votre commande",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous commentez une boisson qui ne se trouve pas dans votre commande"},
                status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.update(instance, serializer.validated_data)
        result = {
            'id': instance.id,
            'reference': instance.reference,
            'comments': NoteCommentsSerializer(instance.comments).data,
            'created_by': UserSerializer(instance.created_by).data,
            'commande': CommandeSerializer(instance.commande).data,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        # Notification du client ou tous les utilisateurs du restaurant
        subject = 'Mise à jour de la note sur la commande ' + str(instance.commande.reference) + ': ' + str(instance.commande.reference)
        message_sms = "Hello! C'est WaziEats, \nLa note a été mise à jour sur la commande " + instance.commande.reference + ".\nMerci de nous faire confiance."
        message_mail = "La note a été mise à jour sur la commande " + instance.commande.reference
        en_tete = 'Mise à jour de la note sur la commande'
        flag = 0
        if user.is_client is True:
            t1 = Thread(
                target=thread_send_notif_restau,
                args=(request, subject, message_sms, message_mail, en_tete, flag, restaurant)
            )
            t1.start()
        else:
            t1 = Thread(
                target=notifications_message,
                args=(request, instance.commande.created_by, subject, message_sms, message_mail, en_tete, flag)
            )
            t1.start()
        logger.info(
            "La note a ete modifie avec succes",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            result,
            status.HTTP_200_OK)
    except Note.DoesNotExist:
        logger.info(
            "La note n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "La note n'existe pas"},
            status=status.HTTP_404_NOT_FOUND)


correct_response_list = openapi.Response(
    description='Liste des notes d\'une commande',
    schema=schema_response_note_list,)


@swagger_auto_schema(method='get',
                     manual_parameters=[restaurant_param, size_param, page_param],
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response_list})
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def list_note(request, commande):
    """Docstring for function."""
    user = request.user
    if user.has_perm('restaurantCommande.view_note') is False and user.is_client is False:
        logger.warning(
            "Vous n'avez pas accès à la liste des notes d'une commande",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la liste des notes d'une commande"},
            status=status.HTTP_403_FORBIDDEN)
    if user.is_client is True:
        restaurant = request.query_params.get('restaurant', None)
        if restaurant is None:
            logger.warning(
                "Paramètre restaurant absent",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Paramètre restaurant absent"},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            restaurant = Restaurant.objects.get(pk=restaurant, is_active=True)
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
        set_tenant_from_restaurant(restaurant)
    else:
        set_tenant(request)

    try:
        com = Commande.objects.get(pk=commande, is_active=True, is_deleted=False)
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

    note = Note.objects.all().filter(commande=com).order_by('-id')
    results = []
    for c in note:
        res = {
            'id': c.id,
            'reference': c.reference,
            'comments': NoteCommentsSerializer(c.comments).data,
            'created_by': UserSerializer(c.created_by).data,
            'commande': CommandeSerializer(c.commande).data,
            'created_at': c.created_at,
            'updated_at': c.updated_at
        }
        results.append(res)
    size = request.query_params.get('size', None)
    page = request.query_params.get('page', None)
    if size is not None and page is not None:
        paginator = Paginator(results, size)
        try:
            results = paginator.page(page).object_list
        except PageNotAnInteger:
            results = paginator.page(1).object_list
        except EmptyPage:
            results = paginator.page(paginator.num_pages).object_list

    logger.info(
        "Liste des notes renvoyées avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(results, status.HTTP_200_OK)

