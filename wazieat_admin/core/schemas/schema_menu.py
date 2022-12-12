from drf_yasg import openapi
from .schema_restaurant_food import *
from .schema_user import *

schema_response_menu = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(title="id", description="Identifiant du menu", type=openapi.TYPE_INTEGER,),
        "reference": openapi.Schema(title="reference", description="Reference du menu", type=openapi.TYPE_STRING,),
        "name": openapi.Schema(title="name", description="Nom du menu", type=openapi.TYPE_STRING,),
        "description": openapi.Schema(title="description", description="Description du menu", type=openapi.TYPE_STRING,),
        "foods": schema_response_food_list,
        "calculated_price": openapi.Schema(title="calculated_price", description="Prix calculé du menu", type=openapi.TYPE_NUMBER,),
        "real_price": openapi.Schema(title="real_price", description="Prix réal du menu", type=openapi.TYPE_STRING,),
        "status_price": openapi.Schema(title="status_price", description="Prix du menu prendre en compte", type=openapi.TYPE_NUMBER,),
        "is_active": openapi.Schema(title="is_active", description="Status d'activation du menu", type=openapi.TYPE_BOOLEAN,),
        "percent": openapi.Schema(title="percent", description="Pourcentage du prix du menu", type=openapi.TYPE_BOOLEAN,),
        "period": openapi.Schema(title="period", description="Période de publication du menu", type=openapi.TYPE_STRING,),
        "created_by": schema_response_user,
    }
)
