import logging
from uuid import uuid4
import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from accounts.models.user import User
from accounts.models.restaurant import Restaurant
from core.tenant import set_tenant_from_restaurant
from restaurantCommande.serializers.note_service import NoteDeliverySerializer
from accounts.serializers.restaurant import RestaurantSerializer
from accounts.serializers.role import RoleSerializer
from restaurantCommande.models.note_service import NoteService
from core.schemas.schema_login import schema_response
from accounts.serializers.init_account import LoginSerializer
from accounts.serializers.user import UserSerializer
from accounts.serializers.delivery import DeliveryClassSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

correct_response = openapi.Response(
    description='Connexion d\'un utilisateur',
    schema=schema_response,)
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


def get_note_service(user):
    """Docstring for function."""
    results = []
    for restaurant in Restaurant.objects.all().filter(is_active=True):
        res = []
        set_tenant_from_restaurant(restaurant)
        notes = NoteService.objects.all().filter(note_delivery__isnull=False)
        for note in notes:
            if note.commande.delivery_validated_by == user:
                res.append(NoteDeliverySerializer(note.note_delivery).data)
        if res:
            val = {
                "restaurant": RestaurantSerializer(restaurant).data,
                "note_delivery": res
            }
            results.append(val)
    return results


class Authview(ObtainAuthToken):
    """Docstring for class."""

    @swagger_auto_schema(request_body=LoginSerializer, responses={200: correct_response, 400: bad_request, 412: error_response})
    def post(self, request,  *args, **kwargs):
        """Docstring for function."""
        try:
            serializer = LoginSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            data = {
                "username": serializer.validated_data['phone'],
                "password": serializer.validated_data['password']
            }
            serializer = self.serializer_class(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            if user.reset_token is not None:
                logger.error(
                    "Veuillez valider votre compte",
                    extra={
                        'restaurant': user.restaurant,
                        'user': user.id
                    }
                )
                return Response(
                    {
                        "message": "Veuillez valider votre compte"
                    },
                    status.HTTP_400_BAD_REQUEST
                )
            if user.password_requested_at is not None:
                if not user.requested_token_valid:
                    logger.error(
                        "Votre mot de passe n'est plus valide",
                        extra={
                            'restaurant': user.restaurant,
                            'user': user.id
                        }
                    )
                    return Response(
                        {
                            "message": "Votre mot de passe n'est plus valide"
                        },
                        status.HTTP_400_BAD_REQUEST
                    )
                user.password_requested_at = None
            user.last_login = datetime.datetime.now()
            user.save()
            token, created = Token.objects.get_or_create(user=user)
            if user.restaurant is None:
                restaurant = ''
                restaurant_id = ''
            else:
                restaurant = user.restaurant.name
                restaurant_id = user.restaurant.id
            if user.is_super():
                role = "superAdmin"
            elif user.is_staff:
                role = "Admin"
            else:
                role = "user"
            roles = []
            for rolex in user.roles.all():
                roles.append(rolex)
            roles = RoleSerializer(roles, many=True).data
            deli = None
            note_livreur = None
            if user.delivery is not None:
                deli = DeliveryClassSerializer(user.delivery).data
                note_livreur = get_note_service(user)
            logger.info(
                "Utilisateur envoyé avec succès.",
                extra={
                    'restaurant': restaurant,
                    'user': user.id
                }
            )
            serializer = UserSerializer(user).data
            picture = None
            if user.picture is not None:
                picture = serializer['picture']

            return Response({
                'token': token.key,
                'user_id': user.pk,
                'phone': user.phone,
                'email': user.email,
                'picture': picture,
                'last_name': user.last_name,
                'first_name': user.first_name,
                'restaurant': restaurant,
                'restaurant_id': restaurant_id,
                'role': role,
                'roles': roles,
                'permissions': user.get_permissions(),
                'is_client': user.is_client,
                'delivery': deli,
                'note_delivery': note_livreur
            })

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

