from django.urls import path
from .views import *
from .views.get_profile_restaurant import get_profile_restaurant

urlpatterns = [
    path('login', Authview.as_view(), name='Connexion'),
    path('admin/user', create_super_admin, name='create_super_admin'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),
    path('logout', Logout.as_view(), name="logout"),
    path('forgot-password', ForgotPassword.as_view(), name="forgot-password"),
    path('verify-token', VerifyToken.as_view(), name="verify-token"),
    path('reset-password', ResetPassword.as_view(), name="verify-password"),
    path('reset-account', InitAccount.as_view(), name="reset-password"),
    path('content-types', ContentView.as_view(), name="content-types"),
    path('permissions', Permissions.as_view(), name="permissions"),
    path('admin/validate/account', admin_validate_account, name="admin_validate_account"),
    path('restaurant/profile/<int:restaurant>/', get_profile_restaurant, name="get_profile_restaurant"),
]
