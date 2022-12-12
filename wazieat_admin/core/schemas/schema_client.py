from drf_yasg import openapi

schema_response_client = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant du client", type=openapi.TYPE_INTEGER,),
        "reference": openapi.Schema(title="reference", description="Reference du client", type=openapi.TYPE_STRING,),
        "phone": openapi.Schema(title="phone", description="Numéro de téléphone du client", type=openapi.TYPE_STRING,),
        "email": openapi.Schema(title="email", description="Email du client", type=openapi.TYPE_STRING,),
        "last_name": openapi.Schema(title="last_name", description="Prénom du client", type=openapi.TYPE_STRING,),
        "first_name": openapi.Schema(title="first_name", description="Nom du client", type=openapi.TYPE_STRING,),
        "is_active": openapi.Schema(title="is_active", description="Status d'activation du client", type=openapi.TYPE_BOOLEAN,),
        "pseudo": openapi.Schema(title="pseudo", description="Pseudo du client", type=openapi.TYPE_STRING,),
        "is_client": openapi.Schema(title="is_client", description="Status du client", type=openapi.TYPE_BOOLEAN,),
    }
)
