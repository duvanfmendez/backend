from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    login_view,
    logout_view,
    profile_view,
    update_profile_view,
    change_password_view,
    register_view,
)

urlpatterns = [
    # Autenticación
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Perfil
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    path('profile/change-password/', change_password_view, name='change_password'),
    
    # Registro (solo admin)
    path('register/', register_view, name='register'),
]