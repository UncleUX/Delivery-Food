from core.tenant import set_tenant
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from restaurantCommande.models.commande import Commande
from restaurantCommande.utils import *


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def commande(request, com):
    """Docstring for function."""
    set_tenant(request)
    commande = Commande.objects.get(pk=com, is_active=True, is_deleted=False)
    value = get_max_time(commande)
    result = {
        'message': value
    }
    return Response(
        result,
        status.HTTP_200_OK)
