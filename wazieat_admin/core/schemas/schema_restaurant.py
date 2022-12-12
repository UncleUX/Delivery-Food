from drf_yasg import openapi

schema_response_restaurant = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant", type=openapi.TYPE_INTEGER,),
        "reference": openapi.Schema(title="reference", description="Reference", type=openapi.TYPE_STRING,),
        "address": openapi.Schema(title="address", description="Adresse", type=openapi.TYPE_STRING,),
        "name": openapi.Schema(title="name", description="Nom", type=openapi.TYPE_STRING,),
        "phone": openapi.Schema(title="phone", description="Numéro de téléphone", type=openapi.TYPE_STRING,),
        "email": openapi.Schema(title="email", description="Email", type=openapi.TYPE_STRING,),
        "rccm": openapi.Schema(title="rccm", description="rccm", type=openapi.TYPE_STRING,),
        "rccm_document": openapi.Schema(title="rccm_document", description="Email", type=openapi.TYPE_STRING,),
        "profile_picture": openapi.Schema(title="profile_picture", description="Email", type=openapi.TYPE_STRING,),
        "picture": openapi.Schema(title="picture", description="Email", type=openapi.TYPE_STRING,),
        "created_at": openapi.Schema(title="created_at", description="Date de création de la commande", type=openapi.TYPE_STRING,),
        "updated_at": openapi.Schema(title="updated_at", description="Date de modification du commande", type=openapi.TYPE_STRING,),
        "module": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
        "drinkType": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
        "drinkCategory": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
        "foodType": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
        "foodCategory": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
        "location": openapi.Schema(title="location", description="Localisation", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_NUMBER)),
    }
)

schema_response_restaurant_list = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(title="id", description="Identifiant", type=openapi.TYPE_INTEGER,),
            "reference": openapi.Schema(title="reference", description="Reference", type=openapi.TYPE_STRING,),
            "address": openapi.Schema(title="address", description="Adresse", type=openapi.TYPE_STRING,),
            "name": openapi.Schema(title="name", description="Nom", type=openapi.TYPE_STRING,),
            "phone": openapi.Schema(title="phone", description="Numéro de téléphone", type=openapi.TYPE_STRING,),
            "email": openapi.Schema(title="email", description="Email", type=openapi.TYPE_STRING,),
            "rccm": openapi.Schema(title="rccm", description="rccm", type=openapi.TYPE_STRING,),
            "rccm_document": openapi.Schema(title="rccm_document", description="Email", type=openapi.TYPE_STRING,),
            "profile_picture": openapi.Schema(title="profile_picture", description="Email", type=openapi.TYPE_STRING,),
            "picture": openapi.Schema(title="picture", description="Email", type=openapi.TYPE_STRING,),
            "created_at": openapi.Schema(title="created_at", description="Date de création de la commande", type=openapi.TYPE_STRING,),
            "updated_at": openapi.Schema(title="updated_at", description="Date de modification du commande", type=openapi.TYPE_STRING,),
            "module": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
            "drinkType": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
            "drinkCategory": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
            "foodType": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
            "foodCategory": openapi.Schema(title="module", description="Identifiant de la commande", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
            "location": openapi.Schema(title="location", description="Localisation", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_NUMBER)),
        }
    ),

)
