from drf_yasg import openapi

schema_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant du commentaire", type=openapi.TYPE_INTEGER,),
        "reference": openapi.Schema(title="reference", description="Reference du commentaire", type=openapi.TYPE_STRING,),
        "comment": openapi.Schema(title="comment", description="Commentaire", type=openapi.TYPE_STRING,),
        "created_at": openapi.Schema(title="created_at", description="Date de création du commentaire", type=openapi.TYPE_STRING,),
        "updated_at": openapi.Schema(title="updated_at", description="Date de modification du commentaire", type=openapi.TYPE_STRING,),
        "menu": openapi.Schema(
            title="menu", description="Menu commenté", type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(title="id", description="Identifiant du menu", type=openapi.TYPE_INTEGER,),
                "reference": openapi.Schema(title="reference", description="Reference du menu", type=openapi.TYPE_STRING,),
                "name": openapi.Schema(title="name", description="Nom du menu", type=openapi.TYPE_STRING,),
                "description": openapi.Schema(title="description", description="Description du menu", type=openapi.TYPE_STRING,),
                "is_active": openapi.Schema(title="is_active", description="Status d'activation du menu", type=openapi.TYPE_BOOLEAN,),
                "calculated_price": openapi.Schema(title="calculated_price", description="Prix calculé du menu", type=openapi.TYPE_INTEGER,),
                "real_price": openapi.Schema(title="real_price", description="Prix réel du menu", type=openapi.TYPE_INTEGER,),
                "status_price": openapi.Schema(title="status_price", description="Prix à considérer", type=openapi.TYPE_INTEGER,),
                "foods": openapi.Schema(title="foods", description="Identifiants des plats", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
                "created_by": openapi.Schema(title="created_by", description="Identifiant de l'utilisateur qui créé le menu", type=openapi.TYPE_INTEGER,),
                "period": openapi.Schema(title="period", description="Période de publication du menu", type=openapi.TYPE_INTEGER,),
            },
        ),
        "client": openapi.Schema(
            title="client", description="Client qui commente", type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(title="id", description="Identifiant du client", type=openapi.TYPE_INTEGER,),
                "reference": openapi.Schema(title="reference", description="Reference du client", type=openapi.TYPE_STRING,),
                "phone": openapi.Schema(title="phone", description="Numéro de téléphone du client", type=openapi.TYPE_STRING,),
                "email": openapi.Schema(title="email", description="Email du client", type=openapi.TYPE_STRING,),
                "last_name": openapi.Schema(title="last_name", description="Prénom du client", type=openapi.TYPE_STRING,),
                "first_name": openapi.Schema(title="first_name", description="Nom du client", type=openapi.TYPE_STRING,),
                "is_active": openapi.Schema(title="is_active", description="Status d'activation du client", type=openapi.TYPE_BOOLEAN,),
                "is_staff": openapi.Schema(title="is_staff", description="Premier status d'administration du client", type=openapi.TYPE_BOOLEAN,),
                "is_admin": openapi.Schema(title="is_admin", description="Second status d'administration du client", type=openapi.TYPE_BOOLEAN,),
                "is_client": openapi.Schema(title="is_client", description="Status du client", type=openapi.TYPE_BOOLEAN,),
                "roles": openapi.Schema(title="roles", description="Identifiant des rôles", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
                "delivery": openapi.Schema(title="delivery", description="Si c'est un livreur", type=openapi.TYPE_INTEGER,),
                "pseudo": openapi.Schema(title="pseudo", description="Pseudo du client", type=openapi.TYPE_STRING,),
            },
        ),
    }
)

schema_response_list = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(title="id", description="Identifiant du menu", type=openapi.TYPE_INTEGER,),
            "reference": openapi.Schema(title="reference", description="Reference du menu", type=openapi.TYPE_STRING,),
            "comment": openapi.Schema(title="name", description="Commentaire", type=openapi.TYPE_STRING,),
            "created_at": openapi.Schema(title="created_at", description="Date de création du commentaire", type=openapi.TYPE_STRING,),
            "updated_at": openapi.Schema(title="updated_at", description="Date de modification du commentaire", type=openapi.TYPE_STRING,),
            "menu": openapi.Schema(
                title="menu", description="Menu commenté", type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(title="id", description="Identifiant du menu", type=openapi.TYPE_INTEGER,),
                    "reference": openapi.Schema(title="reference", description="Reference du menu", type=openapi.TYPE_STRING,),
                    "name": openapi.Schema(title="name", description="Nom du menu", type=openapi.TYPE_STRING,),
                    "description": openapi.Schema(title="description", description="Description du menu", type=openapi.TYPE_STRING,),
                    "is_active": openapi.Schema(title="is_active", description="Status d'activation du menu", type=openapi.TYPE_BOOLEAN,),
                    "calculated_price": openapi.Schema(title="calculated_price", description="Prix calculé du menu", type=openapi.TYPE_INTEGER,),
                    "real_price": openapi.Schema(title="real_price", description="Prix réel du menu", type=openapi.TYPE_INTEGER,),
                    "status_price": openapi.Schema(title="status_price", description="Prix à considérer", type=openapi.TYPE_INTEGER,),
                    "foods": openapi.Schema(title="foods", description="Identifiants des plats", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
                    "created_by": openapi.Schema(title="created_by", description="Identifiant de l'utilisateur qui créé le menu", type=openapi.TYPE_INTEGER,),
                    "period": openapi.Schema(title="period", description="Période de publication du menu", type=openapi.TYPE_INTEGER,),
                },
            ),
            "client": openapi.Schema(
                title="client", description="Client qui commente", type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(title="id", description="Identifiant du plat", type=openapi.TYPE_INTEGER,),
                    "reference": openapi.Schema(title="reference", description="Reference du plat", type=openapi.TYPE_STRING,),
                    "phone": openapi.Schema(title="phone", description="Numéro de téléphone du client", type=openapi.TYPE_STRING,),
                    "email": openapi.Schema(title="email", description="Email du client", type=openapi.TYPE_STRING,),
                    "last_name": openapi.Schema(title="last_name", description="Prénom du client", type=openapi.TYPE_STRING,),
                    "first_name": openapi.Schema(title="first_name", description="Nom du client", type=openapi.TYPE_STRING,),
                    "is_active": openapi.Schema(title="is_active", description="Status d'activation du client", type=openapi.TYPE_BOOLEAN,),
                    "is_staff": openapi.Schema(title="is_staff", description="Premier status d'administration du client", type=openapi.TYPE_BOOLEAN,),
                    "is_admin": openapi.Schema(title="is_admin", description="Second status d'administration du client", type=openapi.TYPE_BOOLEAN,),
                    "is_client": openapi.Schema(title="is_client", description="Status du client", type=openapi.TYPE_BOOLEAN,),
                    "roles": openapi.Schema(title="roles", description="Identifiant des rôles", type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),),
                    "delivery": openapi.Schema(title="delivery", description="Si c'est un livreur", type=openapi.TYPE_INTEGER,),
                    "pseudo": openapi.Schema(title="pseudo", description="Pseudo du client", type=openapi.TYPE_STRING,),
                },
            ),
        }
    )
)
