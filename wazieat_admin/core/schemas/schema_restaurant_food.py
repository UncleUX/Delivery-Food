from drf_yasg import openapi
from .schema_user import *

schema_response_food_list = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_OBJECT,
        title="drink",
        description="Informations d'une boisson d'un restaurant",
        properties={
            "id": openapi.Schema(title="id", description="Identifiant", type=openapi.TYPE_INTEGER,),
            "reference": openapi.Schema(title="reference", description="reference", type=openapi.TYPE_STRING,),
            "name": openapi.Schema(title="name", description="Nom", type=openapi.TYPE_STRING,),
            "description": openapi.Schema(title="description", description="Description", type=openapi.TYPE_STRING,),
            "is_active": openapi.Schema(title="is_active", description="Status d'activation", type=openapi.TYPE_BOOLEAN,),
            "foodType": openapi.Schema(title="foodType", description="Type de plats", type=openapi.TYPE_INTEGER,),
            "foodCategory": openapi.Schema(title="foodCategory", description="Catégorie du plats", type=openapi.TYPE_INTEGER,),
            "foodPicture": openapi.Schema(title="foodPicture", description="Chemin de la photo", type=openapi.TYPE_STRING,),
            "origin": openapi.Schema(title="origin", description="Origine", type=openapi.TYPE_STRING,),
            "ingredients": openapi.Schema(title="ingredients", description="Identifiants des ingredients", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            "price": openapi.Schema(title="price", description="Prix", type=openapi.TYPE_INTEGER,),
            "created_by": schema_response_user,
        }
    ),

)
