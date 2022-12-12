from django.urls import path
from .views.client import list_menu
from .views.comments import list_comment, change_comment, create_comment


urlpatterns = [
    path('client/menu/<int:restaurant>/', list_menu, name='list_menu'),
    path('client/comment/menu/<int:menu>', list_comment, name='list_comment'),
    path('client/comment/<int:comment>', change_comment, name='change_comment'),
    path('client/comment/menu', create_comment, name='create_comment'),
]
