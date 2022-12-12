import logging
import datetime
from rest_framework.response import Response
from rest_framework import status
from core.tenant import set_tenant_from_restaurant, set_tenant
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from restaurantMenu.serializers.comments import CommentsSerializer, CommentsCreateSerializer
from restaurantMenu.models.comments import Comments
from core.schemas.schema_comment import schema_response, schema_response_list
from accounts.serializers.user import UserSerializer
from accounts.models.restaurant import Restaurant
from restaurantMenu.serializers.menu import MenuSerializer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger("myLogger")

restaurant_param = openapi.Parameter('restaurant', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER, required=True)
page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER)
size_param = openapi.Parameter('size', openapi.IN_QUERY, description="Identifiant du restaurant du menu", type=openapi.TYPE_INTEGER)

correct_response = openapi.Response(
    description='Créer un commentaire sur un menu du restaurant',
    schema=schema_response,)
forbidden_request = openapi.Response('Pas de permissions')
bad_request = openapi.Response('Message de mauvaise requête')
error_response = openapi.Response('Message d\'erreur')


@swagger_auto_schema(method='post',
                     request_body=CommentsCreateSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response, 412: error_response})
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def create_comment(request):
    """Docstring for function."""
    user = request.user
    if user.is_client is False:
        logger.error(
            {'message': "seuls les clients peuvent faire des commentaires"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "seuls les clients peuvent faire des commentaires"},
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
    set_tenant_from_restaurant(restaurant)
    serializer = CommentsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    com = serializer.save(client=user)
    result = {
        'id': com.id,
        'reference': com.reference,
        'comment': com.comment,
        'client': UserSerializer(com.client).data,
        'menu': MenuSerializer(com.menu).data,
        'created_at': com.created_at,
        'updated_at': com.updated_at
    }
    logger.info(
        "Le commentaire a ete cree avec succès",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(
        result,
        status.HTTP_201_CREATED)


correct_response_change = openapi.Response(
    description='Modifier un commentaire sur un menu du restaurant',
    schema=schema_response,)


@swagger_auto_schema(method='put',
                     request_body=CommentsCreateSerializer,
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response_change, 412: error_response})
@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def change_comment(request, comment):
    """Docstring for function."""
    user = request.user
    if user.is_client is False:
        logger.error(
            {'message': "seuls les clients peuvent modifier des commentaires"},
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "seuls les clients peuvent modifier des commentaires"},
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
        set_tenant_from_restaurant(restaurant)
        instance = Comments.objects.get(pk=comment)
        serializer = CommentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if instance.menu != serializer.validated_data['menu']:
            logger.info(
                "Ce commentaire appartient a un autre menu",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Ce commentaire appartient a un autre menu"},
                status=status.HTTP_400_BAD_REQUEST)
        if user != instance.client:
            logger.info(
                "Impossible de modifier le commentaire d'un autre client",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
            return Response(
                {'message': "Impossible de modifier le commentaire d'un autre client"},
                status=status.HTTP_400_BAD_REQUEST)
        instance.comment = serializer.validated_data['comment']
        instance.save()
        result = {
            'id': instance.id,
            'reference': instance.reference,
            'comment': instance.comment,
            'client': UserSerializer(instance.client).data,
            'menu': MenuSerializer(instance.menu).data,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        logger.info(
            "Le commentaire a ete modifie avec succes",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            result,
            status.HTTP_200_OK)
    except Comments.DoesNotExist:
        logger.info(
            "Le commentaire n'existe pas",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Le commentaire n'existe pas"},
            status=status.HTTP_404_NOT_FOUND)


correct_response_list = openapi.Response(
    description='Liste les commentaires d\'un menu d\'un restaurant',
    schema=schema_response_list,)


@swagger_auto_schema(method='get',
                     manual_parameters=[restaurant_param, page_param, size_param],
                     responses={403: forbidden_request, 400: bad_request, 200: correct_response_list, 412: error_response})
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def list_comment(request, menu):
    """Docstring for function."""
    user = request.user
    if user.has_perm('restaurantMenu.view_comments') is False and user.is_client is False:
        logger.warning(
            "Vous n'avez pas accès à la liste des commentaires d'un menu",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
        return Response(
            {'message': "Vous n'avez pas accès à la liste des commentaires d'un menu"},
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
    com = Comments.objects.all().filter(menu=menu)
    results = []
    for c in com:
        res = {
            'id': c.id,
            'reference': c.reference,
            'comment': c.comment,
            'client': UserSerializer(c.client).data,
            'menu': MenuSerializer(c.menu).data,
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
        "Liste des commentaires renvoyés avec succes",
        extra={
            'restaurant': user.restaurant,
            'user': user.id
        }
    )
    return Response(results, status.HTTP_200_OK)

