from drf_yasg import openapi
from .schema_user import *
from .schema_commande import *

schema_response_note = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant de la note", type=openapi.TYPE_INTEGER,),
        "reference": openapi.Schema(title="reference", description="Reference de la note", type=openapi.TYPE_STRING,),
        "message": openapi.Schema(title="message", description="Contenu du commentaire", type=openapi.TYPE_STRING,),
        "commande": schema_response_commande,
        "created_by": schema_response_user,
        "created_at": openapi.Schema(title="created_at", description="Date de création de la note", type=openapi.TYPE_STRING,),
        "updated_at": openapi.Schema(title="updated_at", description="Date de modification de la note", type=openapi.TYPE_STRING,),
    }
)

schema_response_note_list = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(title="id", description="Identifiant de la note", type=openapi.TYPE_INTEGER,),
            "reference": openapi.Schema(title="reference", description="Reference de la note", type=openapi.TYPE_STRING,),
            "message": openapi.Schema(title="message", description="Contenu du commentaire", type=openapi.TYPE_STRING,),
            "commande": schema_response_commande,
            "created_by": schema_response_user,
            "created_at": openapi.Schema(title="created_at", description="Date de création de la note", type=openapi.TYPE_STRING,),
            "updated_at": openapi.Schema(title="updated_at", description="Date de modification de la note", type=openapi.TYPE_STRING,),
        }
    ),

)


