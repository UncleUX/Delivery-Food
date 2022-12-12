from drf_yasg import openapi

schema_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "token": openapi.Schema(title="token", description="Token", type=openapi.TYPE_STRING,),
        "user_id": openapi.Schema(title="user_id", description="Identifiant", type=openapi.TYPE_INTEGER,),
        "phone": openapi.Schema(title="phone", description="Numéro de téléphone", type=openapi.TYPE_STRING,),
        "email": openapi.Schema(title="email", description="Adresse mail", type=openapi.TYPE_STRING,),
        "last_name": openapi.Schema(title="last_name", description="Nom", type=openapi.TYPE_STRING,),
        "first_name": openapi.Schema(title="first_name", description="Prénom", type=openapi.TYPE_STRING,),
        "restaurant": openapi.Schema(title="restaurant", description="Nom du restaurant", type=openapi.TYPE_STRING,),
        "role": openapi.Schema(title="role", description="Rôle", type=openapi.TYPE_STRING,),
        "roles": openapi.Schema(title="roles", description="Listes des noms des rôles", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),),
        "permissions": openapi.Schema(title="permissions", description="Liste des permissions", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "is_client": openapi.Schema(title="is_client", description="Status de vérification du client", type=openapi.TYPE_BOOLEAN,),
        "delivery": openapi.Schema(title="delivery", description="Identifiant du livreur", type=openapi.TYPE_INTEGER,),
    }
)
