"""
User Service URLs
Handles: login, logout, register, user profile
"""
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/user/', views.api_user_info, name='api_user_info'),
    path('api/validate-token/', views.api_validate_token, name='api_validate_token'),
    
    # Web endpoints (for template rendering)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Health check
    path('health/', views.health_check, name='health'),
]
