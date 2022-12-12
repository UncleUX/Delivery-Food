import logging
import datetime
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant_from_restaurant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantCommande.models.note_service import NoteService
from accounts.models.restaurant import Restaurant
from restaurantCommande.models.commande import Commande
from restaurantCommande.models.note import Note
from django.db import connection
from core.schemas.schema_note_service import schema_response_note_service
from accounts.models.user import User
from restaurantCommande.serializers.note_service import (NoteServiceSerializer, NoteServiceCreateSerializer,
                                                         NoteDeliverySerializer, NoteRestaurantSerializer)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from restaurantCommande.utils import *

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Note du service par le client',
    schema=schema_response_note_service)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


@swagger_auto_schema(method='post',
                     request_body=NoteServiceCreateSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response, 412: error_response})
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def create_note_service(request):
    """Docstring for function."""
    user = request.user
    restaurant = None
    # Gestion des tenants en fonction des utilisateurs
    if user.is_client is True:
        try:
            restaurant = Restaurant.objects.get(pk=request.data['restaurant'], is_active=True)
        except Restaurant.DoesNotExist:
            logger.warning(
                "Un restaurant avec cette clé primaire n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Un restaurant avec cette clé primaire n'existe pas"},
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
    serializer = NoteServiceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if check_foods_note(serializer) is False:
        logger.warning(
            "Vous notez un plat qui ne se trouve pas dans votre commande",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous notez un plat qui ne se trouve pas dans votre commande"},
            status=status.HTTP_400_BAD_REQUEST)
    if check_drinks_note(serializer) is False:
        logger.warning(
            "Vous notez une boisson qui ne se trouve pas dans votre commande",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous notez une boisson qui ne se trouve pas dans votre commande"},
            status=status.HTTP_400_BAD_REQUEST)
    commande = serializer.validated_data['commande']
    if commande.created_by != user:
        logger.warning(
            "Vous pouvez pas noter une commande dont vous n'êtes pas l'auteur",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous pouvez pas noter une commande dont vous n'êtes pas l'auteur"},
            status=status.HTTP_400_BAD_REQUEST)
    count = NoteService.objects.all().filter(commande=commande).count()
    if count > 0:
        logger.warning(
            "Vous avez deja noté cette commande",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous avez deja noté cette commande"},
            status=status.HTTP_400_BAD_REQUEST)
    note = serializer.save(created_by=user)
    result = {
        'id': note.id,
        'reference': note.reference,
        'note_delivery': NoteDeliverySerializer(note.note_delivery).data,
        'note_restaurant': NoteRestaurantSerializer(note.note_restaurant).data,
        'created_by': UserSerializer(note.created_by).data,
        'commande': CommandeSerializer(note.commande).data,
        'created_at': note.created_at,
        'updated_at': note.updated_at
    }

    logger.info(
        "La note a été crée avec succès",
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
    schema=schema_response_note_service,)


@swagger_auto_schema(method='put',
                     request_body=NoteServiceCreateSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response_change, 412: error_response})
@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def change_note_service(request, note):
    """Docstring for function."""
    user = request.user
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
    try:
        instance = NoteService.objects.get(pk=note)
        serializer = NoteServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if instance.commande != serializer.validated_data['commande']:
            logger.info(
                "Cette note appartient à une autre commande",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Cette note appartient à une autre commande"},
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
        if check_foods_note(serializer) is False:
            logger.warning(
                "Vous notez un plat qui ne se trouve pas dans votre commande",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous notez un plat qui ne se trouve pas dans votre commande"},
                status=status.HTTP_400_BAD_REQUEST)
        if check_drinks_note(serializer) is False:
            logger.warning(
                "Vous notez une boisson qui ne se trouve pas dans votre commande",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous notez une boisson qui ne se trouve pas dans votre commande"},
                status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.update(instance, serializer.validated_data)
        result = {
            'id': instance.id,
            'reference': instance.reference,
            'note_delivery': NoteDeliverySerializer(instance.note_delivery).data,
            'note_restaurant': NoteRestaurantSerializer(instance.note_restaurant).data,
            'created_by': UserSerializer(instance.created_by).data,
            'commande': CommandeSerializer(instance.commande).data,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }

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
    except NoteService.DoesNotExist:
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

