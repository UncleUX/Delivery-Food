from drf_yasg import openapi

schema_response_delivery = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant du livreur", type=openapi.TYPE_INTEGER,),
        "reference": openapi.Schema(title="reference", description="Reference du livreur", type=openapi.TYPE_STRING,),
        "phone": openapi.Schema(title="phone", description="Numéro de téléphone du livreur", type=openapi.TYPE_STRING,),
        "email": openapi.Schema(title="email", description="Email du livreur", type=openapi.TYPE_STRING,),
        "last_name": openapi.Schema(title="last_name", description="Prénom du livreur", type=openapi.TYPE_STRING,),
        "first_name": openapi.Schema(title="first_name", description="Nom du livreur", type=openapi.TYPE_STRING,),
        "is_active": openapi.Schema(title="is_active", description="Status d'activation du livreur", type=openapi.TYPE_BOOLEAN,),
        "is_client": openapi.Schema(title="is_client", description="Status du livreur", type=openapi.TYPE_BOOLEAN,),
        "pseudo": openapi.Schema(title="pseudo", description="Pseudo du livreur", type=openapi.TYPE_STRING,),
        "delivery": openapi.Schema(
            title="delivery", description="Informations du livreur", type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(title="id", description="Identifiant", type=openapi.TYPE_INTEGER,),
                "date_of_birth": openapi.Schema(title="reference", description="Date de naissance", type=openapi.TYPE_STRING,),
                "scan_cni": openapi.Schema(title="phone", description="Document scanné de la CNI", type=openapi.TYPE_STRING,),
                "address": openapi.Schema(title="email", description="Adresse", type=openapi.TYPE_STRING,),
                "brand": openapi.Schema(title="last_name", description="Marque de la moto", type=openapi.TYPE_STRING,),
                "model": openapi.Schema(title="first_name", description="Modèle de la moto", type=openapi.TYPE_STRING,),
                "has_permis": openapi.Schema(title="is_active", description="Status de la possession du permis", type=openapi.TYPE_BOOLEAN,),
                "has_motor": openapi.Schema(title="has_motor", description="Status de la possession de la moto", type=openapi.TYPE_BOOLEAN,),
                "power": openapi.Schema(title="power", description="Puissance de la moto", type=openapi.TYPE_STRING,),
                "location": openapi.Schema(title="location", description="Localisation", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_NUMBER)),
            },
        ),
    }
)
