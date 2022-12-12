import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from accounts.serializers.user import UserSerializer
from accounts.models.user import User

logger = logging.getLogger("myLogger")


@api_view(['POST'])
def create_super_admin(request):
    """Docstring for function."""
    email = "admin@local.com"
    phone = "+4465565652"
    try:
        user = User.objects.get(email=email)
        logger.info(
            "Super admin existant!",
            extra={
                'restaurant': None,
                'user': None
            }
        )
    except User.DoesNotExist:
        # Don't need to choose a restaurant id for superuser
        user = User.objects.create_superuser(
            phone=phone,
            email=email,          # email
            last_name="Admin",        # last_name
            first_name="admin",        # first_name
            password='superadmin'    # password
        )
        logger.info(
            "Super admin créé avec succès!",
            extra={
                'restaurant': None,
                'user': user.id
            }
        )

    return Response(UserSerializer(user).data)
