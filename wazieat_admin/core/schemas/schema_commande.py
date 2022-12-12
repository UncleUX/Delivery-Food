from drf_yasg import openapi
from .schema_delivery import *
from .schema_client import *
from .schema_restaurant_drink import *
from .schema_restaurant_food import *
from .schema_menu import *
from .schema_user import *


schema_response_commande = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant de la commande", type=openapi.TYPE_INTEGER,),
        "reference": openapi.Schema(title="reference", description="reference de la commande", type=openapi.TYPE_STRING,),
        "food": schema_response_food_list,
        "drink": schema_response_drink_list,
        "menu": schema_response_menu,
        "created_by": schema_response_client,
        "is_active": openapi.Schema(title="is_active", description="Status d'activation de la commande", type=openapi.TYPE_BOOLEAN,),
        "total_price": openapi.Schema(title="total_price", description="Prix total de la commande", type=openapi.TYPE_NUMBER,),
        "created_at": openapi.Schema(title="created_at", description="Date de création de la commande", type=openapi.TYPE_STRING,),
        "updated_at": openapi.Schema(title="updated_at", description="Date de modification du commande", type=openapi.TYPE_STRING,),
        "is_restaurant_valid": openapi.Schema(title="is_restaurant_valid", description="Status de validation de la commande par le restaurant", type=openapi.TYPE_BOOLEAN,),
        "is_delivery_valid": openapi.Schema(title="is_delivery_valid", description="Status de validation de la commande par le livreur", type=openapi.TYPE_BOOLEAN,),
        "is_delivery_check": openapi.Schema(title="is_delivery_check", description="Status de vérification de la commande par le livreur", type=openapi.TYPE_BOOLEAN,),
        "restaurant_validate_date": openapi.Schema(title="restaurant_validate_date", description="Date de validation de la commande par le restaurant", type=openapi.TYPE_STRING,),
        "delivery_validate_date": openapi.Schema(title="delivery_validate_date", description="Date de validation de la commande par le livreur", type=openapi.TYPE_STRING,),
        "token": openapi.Schema(title="token", description="Code de la commande", type=openapi.TYPE_STRING,),
        "restaurant_cancel_date": openapi.Schema(title="restaurant_cancel_date", description="Date de rejet de la validation de la commande par le restaurant", type=openapi.TYPE_STRING,),
        "delivery_cancel_date": openapi.Schema(title="delivery_cancel_date", description="Date de rejet de la validation de la commande par le livreur", type=openapi.TYPE_STRING,),
        "delivery_check_date": openapi.Schema(title="delivery_check_date", description="Date de vérification de la commande par le livreur", type=openapi.TYPE_STRING,),
        "delivery_date": openapi.Schema(title="delivery_date", description="Date de livraison de la commande", type=openapi.TYPE_STRING,),
        "status": openapi.Schema(title="status", description="Status de la commande", type=openapi.TYPE_INTEGER,),
        "delivery_location": openapi.Schema(title="delivery_location", description="Localisation du livreur", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_NUMBER)),
        "site_delivery": openapi.Schema(title="site_delivery", description="Site de livraison de la commande", type=openapi.TYPE_STRING,),
        "cooking_time": openapi.Schema(title="cooking_time", description="Temps de cuisson de la commande", type=openapi.TYPE_STRING,),
        "restaurant_validated_by": schema_response_user,
        "delivery_validated_by": schema_response_delivery,
        "restaurant_cancel_validated_by": schema_response_user,
        "delivery_cancel_validated_by": schema_response_delivery,
        "notes": openapi.Schema(
            title="notes", description="Notes de la commande", type=openapi.TYPE_ARRAY,
            items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(title="id", description="Identifiant", type=openapi.TYPE_INTEGER,),
                    "reference": openapi.Schema(title="reference", description="Reference", type=openapi.TYPE_STRING,),
                    "message": openapi.Schema(title="phone", description="Contenu de la note", type=openapi.TYPE_STRING,),
                    "commande": openapi.Schema(title="commande", description="Identifiant de la commande", type=openapi.TYPE_INTEGER,),
                    "created_by": openapi.Schema(title="created_by", description="Identifiant de l'utilisateur qui a laissé la note", type=openapi.TYPE_INTEGER,),
                    "created_at": openapi.Schema(title="created_at", description="Date de création", type=openapi.TYPE_STRING,),
                    "updated_at": openapi.Schema(title="updated_at", description="Date de modification", type=openapi.TYPE_STRING,),
                },
            )
        ),
    }
)


schema_response_commande_list = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(title="id", description="Identifiant de la commande", type=openapi.TYPE_INTEGER,),
            "reference": openapi.Schema(title="reference", description="reference de la commande", type=openapi.TYPE_STRING,),
            "food": schema_response_food_list,
            "drink": schema_response_drink_list,
            "menu": schema_response_menu,
            "created_by": schema_response_client,
            "is_active": openapi.Schema(title="is_active", description="Status d'activation de la commande", type=openapi.TYPE_BOOLEAN,),
            "total_price": openapi.Schema(title="total_price", description="Prix total de la commande", type=openapi.TYPE_NUMBER,),
            "created_at": openapi.Schema(title="created_at", description="Date de création de la commande", type=openapi.TYPE_STRING,),
            "updated_at": openapi.Schema(title="updated_at", description="Date de modification du commande", type=openapi.TYPE_STRING,),
            "is_restaurant_valid": openapi.Schema(title="is_restaurant_valid", description="Status de validation de la commande par le restaurant", type=openapi.TYPE_BOOLEAN,),
            "is_delivery_valid": openapi.Schema(title="is_delivery_valid", description="Status de validation de la commande par le livreur", type=openapi.TYPE_BOOLEAN,),
            "is_delivery_check": openapi.Schema(title="is_delivery_check", description="Status de vérification de la commande par le livreur", type=openapi.TYPE_BOOLEAN,),
            "restaurant_validate_date": openapi.Schema(title="restaurant_validate_date", description="Date de validation de la commande par le restaurant", type=openapi.TYPE_STRING,),
            "delivery_validate_date": openapi.Schema(title="delivery_validate_date", description="Date de validation de la commande par le livreur", type=openapi.TYPE_STRING,),
            "token": openapi.Schema(title="token", description="Code de la commande", type=openapi.TYPE_STRING,),
            "restaurant_cancel_date": openapi.Schema(title="restaurant_cancel_date", description="Date de rejet de la validation de la commande par le restaurant", type=openapi.TYPE_STRING,),
            "delivery_cancel_date": openapi.Schema(title="delivery_cancel_date", description="Date de rejet de la validation de la commande par le livreur", type=openapi.TYPE_STRING,),
            "delivery_check_date": openapi.Schema(title="delivery_check_date", description="Date de vérification de la commande par le livreur", type=openapi.TYPE_STRING,),
            "delivery_date": openapi.Schema(title="delivery_date", description="Date de livraison de la commande", type=openapi.TYPE_STRING,),
            "status": openapi.Schema(title="status", description="Status de la commande", type=openapi.TYPE_INTEGER,),
            "delivery_location": openapi.Schema(title="delivery_location", description="Localisation du livreur", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_NUMBER)),
            "restaurant_validated_by": schema_response_user,
            "delivery_validated_by": schema_response_delivery,
            "restaurant_cancel_validated_by": schema_response_user,
            "delivery_cancel_validated_by": schema_response_delivery,
            "notes": openapi.Schema(
                title="notes", description="Notes de la commande", type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(title="id", description="Identifiant", type=openapi.TYPE_INTEGER,),
                        "reference": openapi.Schema(title="reference", description="Reference", type=openapi.TYPE_STRING,),
                        "message": openapi.Schema(title="phone", description="Contenu de la note", type=openapi.TYPE_STRING,),
                        "commande": openapi.Schema(title="commande", description="Identifiant de la commande", type=openapi.TYPE_INTEGER,),
                        "created_by": openapi.Schema(title="created_by", description="Identifiant de l'utilisateur qui a laissé la note", type=openapi.TYPE_INTEGER,),
                        "created_at": openapi.Schema(title="created_at", description="Date de création", type=openapi.TYPE_STRING,),
                        "updated_at": openapi.Schema(title="updated_at", description="Date de modification", type=openapi.TYPE_STRING,),
                    },
                )
            ),
        }
    )
)
