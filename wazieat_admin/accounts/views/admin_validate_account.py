import logging
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from notifications.notifications_activate_delivery import notifications as notif_act
from notifications.notifications_desactivate_delivery import notifications as notif_desact
from rest_framework import status
from django.db import connection
from accounts.models.restaurant import Restaurant
from accounts.models.user import User
from accounts.serializers.admin_validate import AdminValidateSerializer


logger = logging.getLogger("myLogger")


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def admin_validate_account(request):
    """Docstring for function."""
    user = request.user

    if user.delivery is None and user.is_super() is False:
        logger.error(
            {'message': "Vous n'avez pas les accès nécessaires."},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas les accès nécessaires."},
            status.HTTP_403_FORBIDDEN)
    connection.set_schema_to_public()
    serializer = AdminValidateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if serializer.validated_data['activate_status'] is False and serializer.validated_data['activate_reason'] is None:
        logger.warning(
            "Vous ne pouvez pas désactivé ou rejeter un compte sans fournir la raison",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous ne pouvez pas désactivé ou rejeter un compte sans fournir la raison"},
            status=status.HTTP_400_BAD_REQUEST)
    if serializer.validated_data['type_account'] == 1:
        obj = "restaurant"
        try:
            objet = Restaurant.objects.get(pk=serializer.validated_data['object_id'])
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
    else:
        obj = "livreur"
        try:
            objet = User.objects.get(pk=serializer.validated_data['object_id'], is_deleted=False, delivery__isnull=False)
        except User.DoesNotExist:
            logger.warning(
                "Un livreur avec cette clé primaire n'existe pas",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Un livreur avec cette clé primaire n'existe pas"},
                status=status.HTTP_400_BAD_REQUEST)

    if serializer.validated_data['activate_status'] is True and objet.is_active is True:
        logger.warning(
            "Ce " + obj + " est déjà activé",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Cet " + obj + " est déjà activé"},
            status=status.HTTP_409_CONFLICT)
    elif serializer.validated_data['activate_status'] is False and objet.is_active is False:
        logger.warning(
            "Cet " + obj + " n'est pas activé",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Cet " + obj + " n'est pas activé"},
            status=status.HTTP_409_CONFLICT)
    objet.is_active = serializer.validated_data['activate_status']
    password = None
    if obj == "livreur":
        password = User.objects.make_random_password()
        objet.set_password(password)
        objet.delivery.activate_date = datetime.now()
        objet.delivery.activate_reason = serializer.validated_data['activate_reason']
        objet.delivery.activate_by = user
        objet.save()
    else:
        objet.activate_date = datetime.now()
        objet.activate_reason = serializer.validated_data['activate_reason']
        objet.activate_by = user
        objet.save()
    if serializer.validated_data['activate_status'] is False:
        message = "Ce " + obj + " a été désactivé avec succès"
    else:
        message = "Ce " + obj + " a été activé avec succès"
    if obj == 'livreur':
        if serializer.validated_data['activate_status'] is False:
            notif_deact(request, objet, objet.activate_reason)
        else:
            notif_act(request, objet, password)
    logger.warning(
        message,
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        {'message': message},
        status=status.HTTP_200_OK)




