"""wazieats URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from accounts.views.module import ModuleViewSet
from accounts.views.delivery import DeliveryViewSet
from accounts.views.client import ClientViewSet
from accounts.views.role import RoleViewSet
from accounts.views.user import UserViewSet
from accounts.views.restaurant import RestaurantViewSet
from drink.views.category import DrinkCategoryViewSet
from food.views.category import FoodCategoryViewSet
from food.views.type import FoodTypeViewSet
from drink.views.type import DrinkTypeViewSet
from restaurantDrink.views.drink import RestaurantDrinkViewSet
from restaurantFood.views.food import RestaurantFoodViewSet
from restaurantFood.views.ingredient import IngredientViewSet
from restaurantMenu.views.publicationPeriod import PublicationPeriodViewSet
from restaurantMenu.views.menu import MenuViewSet
from restaurantCommande.views.commande import CommandeViewSet
from food.views.food_picture import FoodPictureViewSet
from drink.views.drink import DrinkViewSet


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.decorators import permission_classes


schema_view = get_schema_view(
   openapi.Info(
      title="Documentation API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.ourapp.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="Test License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()
router.register(r'admin/modules', ModuleViewSet)
router.register(r'admin/drink/category', DrinkCategoryViewSet)
router.register(r'admin/drink/type', DrinkTypeViewSet, 'drink_type')
router.register(r'admin/food/category', FoodCategoryViewSet)
router.register(r'admin/food/type', FoodTypeViewSet)
router.register(r'drink', RestaurantDrinkViewSet)
router.register(r'food', RestaurantFoodViewSet)
router.register(r'ingredient', IngredientViewSet)
router.register(r'menu/publication/period', PublicationPeriodViewSet)
router.register(r'menu', MenuViewSet)
router.register(r'commande', CommandeViewSet)
router.register(r'delivery', DeliveryViewSet)
router.register(r'client', ClientViewSet)
router.register(r'role', RoleViewSet)
router.register(r'user', UserViewSet)
router.register(r'restaurant', RestaurantViewSet)
router.register(r'admin/food/picture', FoodPictureViewSet)
router.register(r'admin/drink', DrinkViewSet)
app_name = 'api'
urlpatterns = [
    path(
        'api/auth/',
        include('rest_framework.urls', namespace="rest_framework")
    ),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('restaurantMenu.urls')),
    path('api/', include('core.urls')),
    path('api/', include('restaurantCommande.urls')),
    path('api/', include('restaurantFood.urls')),
    path('api/', include('restaurantDrink.urls')),
    path('api/', include('food.urls')),
    path('api/', include((router.urls, 'api'))),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
