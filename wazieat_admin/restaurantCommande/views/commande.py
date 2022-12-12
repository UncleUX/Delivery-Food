import logging
import decimal
from datetime import datetime, timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from core.tenant import set_tenant, set_tenant_from_restaurant
from restaurantCommande.serializers.commande import CommandeSerializer, CommandeCreateSerializer
from restaurantCommande.serializers.note import NoteSerializer
from restaurantMenu.models.menu import Menu
from restaurantCommande.models.commande import Commande
from accounts.models.restaurant import Restaurant
from restaurantCommande.models.note import Note
from notifications.notifications_message import notifications_message
from notifications.notif_cancel_commande import notif_cancel_commande
from core.schemas.schema_commande import schema_response_commande, schema_response_commande_list
from django.db.models import Q
from geopy import distance
from django.conf import settings
from accounts.models.user import User
from threading import Thread
from restaurantCommande.utils import *

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


logger = logging.getLogger("myLogger")

restaurant_param = openapi.Parameter('restaurant', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER, required=True)

correct_response = openapi.Response(description='Création/Modification/Visualisation d\'une commande', schema=schema_response_commande,)

correct_response_list = openapi.Response(description='Liste des commandes', schema=schema_response_commande_list,)

forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


class CommandeViewSet(viewsets.ModelViewSet):
    """Docstring for class."""

    permission_classes = [IsAuthenticated]

    queryset = Commande.objects.all().filter(is_deleted=False).order_by('id')
    serializer_class = CommandeSerializer

    @swagger_auto_schema(
        manual_parameters=[restaurant_param],
        responses={403: forbidden_request, 400: bad_request, 200: correct_response_list})
    def list(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantCommande.view_commande') is False and user.is_client is False and user.delivery is False:
            logger.warning(
                "Vous n'avez pas accès à la liste des commandes",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la liste des commandes"},
                status=status.HTTP_403_FORBIDDEN)

        if user.is_client is True or user.delivery is True:
            restaurant = self.request.query_params.get('restaurant', None)
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
            queryset = Commande.objects.all().filter(created_by=user, is_active=True, is_deleted=False).order_by('id')

        else:
            set_tenant(request)
            restaurant = user.restaurant
            queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        result = []
        for s in serializer.data:
            commande = Commande.objects.get(pk=s['id'])
            notes = Note.objects.all().filter(commande=commande).order_by('-id')
            data = get_commande(commande, notes, restaurant)
            # Same price
            data['food_same_price'] = get_food_same_price(commande)
            data['drink_same_price'] = get_drink_same_price(commande)
            result.append(data)

        if page is not None:
            return self.get_paginated_response(result)

        logger.info(
            "Liste des commandes renvoyés avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )

        return Response(result)

    @swagger_auto_schema(
        manual_parameters=[restaurant_param],
        responses={403: forbidden_request, 400: bad_request, 200: correct_response})
    def retrieve(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.has_perm('restaurantCommande.view_commande') is False and user.is_client is False and user.delivery is False:
            logger.warning(
                "Vous n'avez pas accès à la visualisation d'une commande.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas accès à la visualisation d'une commande."},
                status=status.HTTP_403_FORBIDDEN)
        restaurant = user.restaurant
        if user.is_client is True or user.delivery is True:
            restaurant = self.request.query_params.get('restaurant', None)
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

        commande = self.get_object()
        notes = Note.objects.all().filter(commande=commande).order_by('-id')
        data = get_commande(commande, notes, restaurant)

        # Same price
        data['food_same_price'] = get_food_same_price(commande)
        data['drink_same_price'] = get_drink_same_price(commande)

        logger.info(
            "commande renvoyée avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(data)

    @swagger_auto_schema(
        request_body=CommandeCreateSerializer,
        responses={403: forbidden_request, 400: bad_request, 200: correct_response, 412: error_response})
    def create(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.is_client is False:
            logger.warning(
                "Vous n'avez pas de droits pour passer une commande",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour passer une commande"},
                status=status.HTTP_403_FORBIDDEN)
        try:
            restaurant = Restaurant.objects.get(pk=self.request.data['restaurant'], is_active=True)
            if restaurant is None:
                logger.warning(
                    "Le champ restaurant ne peut être null",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Le champ restaurant ne peut être null"},
                    status=status.HTTP_400_BAD_REQUEST)
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
            set_tenant_from_restaurant(restaurant)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            ser = None
            commande = self.perform_create(serializer, user=user)
            commande.total_price = get_total_price(commande)
            commande.cooking_time = get_max_time(commande)
            commande.save()
            # Creation de la note de la commande
            try:
                message = self.request.data['note']
                if message is not None:
                    message['commande'] = commande.id
                    message['restaurant'] = restaurant.id
                    ser = NoteSerializer(data=message)
                    ser.is_valid(raise_exception=True)
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
            except KeyError:
                pass
            val = None
            if ser is not None:
                val = ser.save(created_by=user)
            headers = self.get_success_headers(serializer.data)
            data = get_commande(commande, val, restaurant)

            # Same price
            data['food_same_price'] = get_food_same_price(commande)
            data['drink_same_price'] = get_drink_same_price(commande)

            subject = 'Nouvelle commande'
            message_sms = "Hello! C'est WaziEats, \nVous avez une nouvelle commande.\nMerci de nous faire confiance."
            message_mail = "Vous avez une nouvelle commande.\nMerci de nous faire confiance."
            en_tete = 'Nouvelle commande'
            flag = 1
            # notifications de tous les utilisateurs du restaurant
            t1 = Thread(
                target=thread_send_notif_restau,
                args=(request, subject, message_sms, message_mail, en_tete, flag, restaurant)
            )

            # notifications de tous les livreurs du restaurant dans un rayon
            t2 = Thread(
                target=thread_send_notif_delivery,
                args=(request, subject, message_sms, message_mail, en_tete, flag, restaurant)
            )

            # Notification Client si commande non validée
            t3 = Thread(
                target=notif_cancel_commande,
                args=(request, commande, user, restaurant)
            )
            t1.start()
            t2.start()
            t3.start()

            logger.info(
                "Commande créée avec succès",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers)

        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)

    def perform_create(self, serializer, user):
        """Docstring for function."""
        set_tenant(self.request)
        return serializer.save(created_by=user)

    @swagger_auto_schema(
        request_body=CommandeCreateSerializer,
        responses={403: forbidden_request, 400: bad_request, 200: correct_response, 412: error_response})
    def update(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.is_client is False:
            logger.warning(
                "Vous n'avez pas de droits pour modifier une commande.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour modifier une commande"},
                status=status.HTTP_403_FORBIDDEN)
        try:
            restaurant = Restaurant.objects.get(pk=self.request.data['restaurant'], is_active=True)
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
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        try:
            serializer = self.get_serializer(
                instance, data=request.data,
                partial=partial)
            serializer.is_valid(raise_exception=True)

            if instance.created_by != user:
                logger.error(
                    "Vous ne pouvez pas modifier la commande d'un autre client",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Vous ne pouvez pas modifier la commande d'un autre client"},
                    status=status.HTTP_409_CONFLICT)
            diff = datetime.now(timezone.utc) - instance.created_at
            if int(diff.total_seconds()) > settings.MAX_TIME['update_commande']*60:
                logger.error(
                    "Vous ne pouvez plus modifier cette commande car elle est en cours de traitement",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Vous ne pouvez plus modifier cette commande car elle est en cours de traitement"},
                    status=status.HTTP_409_CONFLICT)
            commande = self.perform_update(serializer)
            commande.total_price = get_total_price(commande)
            commande.save()
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            note = Note.objects.all().filter(commande=commande)
            data = get_commande(commande, note, restaurant)
            # Same price
            data['food_same_price'] = get_food_same_price(commande)
            data['drink_same_price'] = get_drink_same_price(commande)
            subject = 'Mise à jour de la commande'
            message_sms = "Hello! C'est WaziEats, \nUne commande vient d'être mise à jour.\nMerci de nous faire confiance."
            message_mail = "Une commande vient d'être mise à jour."
            en_tete = 'Mise à jour de la commande'
            flag = 1
            # notifications de tous les utilisateurs du restaurant
            t1 = Thread(
                target=thread_send_notif_restau,
                args=(request, subject, message_sms, message_mail, en_tete, flag, restaurant)
            )
            t1.start()

            logger.info(
                "Mise à jour de la commande réussie!",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(data)

        except Exception as e:
            logger.error(
                str(e),
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': str(e)},
                status=status.HTTP_412_PRECONDITION_FAILED)

    def perform_update(self, serializer):
        """Docstring for function."""
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Docstring for function."""
        user = self.request.user
        if user.is_client is False:
            logger.warning(
                "Vous n'avez pas de droits pour supprimer une commande.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Vous n'avez pas de droits pour supprimer une commande"},
                status=status.HTTP_403_FORBIDDEN)
        restaurant = self.request.query_params.get('restaurant', None)
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

        try:
            set_tenant_from_restaurant(restaurant)
            instance = Commande.objects.filter(
                is_deleted=False, pk=kwargs['pk']).get()
            if instance.created_by != user:
                logger.error(
                    "Vous ne pouvez pas annuler la commande d'un autre client",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {'message': "Vous ne pouvez pas annuler la commande d'un autre client"},
                    status=status.HTTP_409_CONFLICT)
            diff = datetime.now(timezone.utc) - instance.created_at
            if int(diff.total_seconds()) > settings.MAX_TIME['delete_commande']*60:
                logger.error(
                    "Vous ne pouvez plus annuler cette commande car elle est en cours de traitement",
                    extra={
                        'restaurant': request.user.restaurant,
                        'user': request.user.id
                    }
                )
                return Response(
                    {'message': "Vous ne pouvez plus annuler cette commande car elle est en cours de traitement"},
                    status=status.HTTP_409_CONFLICT)

            self.perform_destroy(instance)

            subject = 'Commande annulée'
            message_sms = "Hello! C'est WaziEats, \nUne commande vient d'être annulée.\nMerci de nous faire confiance."
            message_mail = "Une commande vient d'être annulée."
            en_tete = 'Commande annulée'
            flag = 1

            # notifications de tous les utilisateurs du restaurant
            t1 = Thread(
                target=thread_send_notif_restau,
                args=(request, subject, message_sms, message_mail, en_tete, flag, restaurant)
            )

            # notifications de tous les livreurs du restaurant dans un rayon
            t2 = Thread(
                target=thread_send_notif_delivery,
                args=(request, subject, message_sms, message_mail, en_tete, flag, restaurant)
            )
            t1.start()
            t2.start()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Commande.DoesNotExist:
            logger.info(
                "La commande à annuler n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "La commande à annuler n'existe pas"},
                status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        """Docstring for function."""
        instance.is_active = False
        instance.is_deleted = True
        instance.status = 6
        instance.save()


def thread_send_notif_restau(request, subject, message_sms, message_mail, en_tete, flag, restaurant):
    """Docstring for function."""
    users = User.objects.all().filter(
        is_deleted=False,
        restaurant=restaurant
    )
    for usr in users:
        notifications_message(request, usr, subject, message_sms, message_mail, en_tete, flag)


def thread_send_notif_delivery(request, subject, message_sms, message_mail, en_tete, flag, restaurant):
    """Docstring for function."""
    center_point = [{'lat': float(restaurant.location[0]), 'lng': float(restaurant.location[1])}]
    radius = settings.RADIUS_NOTIF_DELIVERY/1000  # in kilometer
    deliveries = User.objects.all().filter(
        is_deleted=False,
        restaurant=None,
        delivery__isnull=False
    )
    for usr in deliveries:
        if usr.delivery.location is not None:
            location = usr.delivery.location
            test_point = [{'lat': location[0], 'lng': location[1]}]
            center_point_tuple = tuple(center_point[0].values())  # (-7.7940023, 110.3656535)
            test_point_tuple = tuple(test_point[0].values())  # (-7.79457, 110.36563)

            dis = distance.distance(center_point_tuple, test_point_tuple).km
            # print("Distance: {}".format(dis))  # Distance: 0.0628380925748918

            if dis <= radius:
                notifications_message(request, usr, subject, message_sms, message_mail, en_tete, flag)
