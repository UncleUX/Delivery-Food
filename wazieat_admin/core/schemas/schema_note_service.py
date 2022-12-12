from drf_yasg import openapi
from .schema_user import *
from .schema_commande import *

schema_response_note_service = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant de la note du service", type=openapi.TYPE_INTEGER,),
        "reference": openapi.Schema(title="reference", description="Reference de la note du service", type=openapi.TYPE_STRING,),
        "note_livreur": openapi.Schema(title="note_livreur", description="note du livreur", type=openapi.TYPE_STRING,),
        "note_restaurant": openapi.Schema(title="note_restaurant", description="note du restaurant", type=openapi.TYPE_STRING,),
        "commande": schema_response_commande,
        "created_by": schema_response_user,
        "created_at": openapi.Schema(title="created_at", description="Date de création de la note", type=openapi.TYPE_STRING,),
        "updated_at": openapi.Schema(title="updated_at", description="Date de modification de la note", type=openapi.TYPE_STRING,),
    }
)
