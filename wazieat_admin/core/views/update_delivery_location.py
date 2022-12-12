import logging
import datetime
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant_from_restaurant, set_tenant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantCommande.serializers.note import NoteSerializer
from restaurantCommande.models.note import Note
from restaurantCommande.serializers.commande import CommandeSerializer
from core.serializers.update_delivery_location import UpdateDeliveryLocationSerializer
from accounts.serializers.user import UserSerializer
from accounts.serializers.delivery import DeliverySerializer
from core.schemas.schema_delivery import schema_response_delivery
from accounts.models.restaurant import Restaurant
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

logger = logging.getLogger("myLogger")

bad_request = openapi.Response('Message de mauvaise requête')

correct_response = openapi.Response(
    description='Modification de la localisation d\'un livreur',
    schema=schema_response_delivery,)


class ChangeDeliveryLocationView(generics.UpdateAPIView):
    """Docstring for class."""

    serializer_class = DeliverySerializer
    http_method_names = ['put']

    @swagger_auto_schema(
        request_body=UpdateDeliveryLocationSerializer,
        responses={400: bad_request, 200: correct_response})
    def put(self, request):
        """Docstring for function."""
        serializer = UpdateDeliveryLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            delivery = User.objects.get(pk=request.data['delivery'])
        except User.DoesNotExist:
            logger.warning(
                "Un livreur avec cette cle primaire n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Un livreur avec cette cle primaire n'existe pas"},
                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            logger.warning(
                "Le champ delivery est absent dans la requête",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Le champ delivery est absent dans la requête"},
                status=status.HTTP_400_BAD_REQUEST)

        delivery.delivery.location = serializer.validated_data['location']
        delivery.delivery.save()

        logger.info(
            "La localisation du livreur a été mise à jour avec succès",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            DeliverySerializer(delivery).data,
            status.HTTP_200_OK)
