"""
API Gateway URLs
Routes requests to appropriate microservices
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    
    # Health check for all services
    path('health/', views.health_check, name='health'),
    path('services/', views.services_status, name='services'),
    
    # Proxy routes - these forward to appropriate services
    # User Service (port 8001)
    path('api/user/login/', views.proxy_user_login, name='proxy_login'),
    path('api/user/register/', views.proxy_user_register, name='proxy_register'),
    path('api/user/logout/', views.proxy_user_logout, name='proxy_logout'),
    
    # Flight Service (port 8002)
    path('api/flights/search/', views.proxy_flight_search, name='proxy_flight_search'),
    path('api/places/', views.proxy_places, name='proxy_places'),
    path('api/places/search/<str:q>/', views.proxy_places_search, name='proxy_places_search'),
    
    # Booking Service (port 8003)
    path('api/bookings/', views.proxy_bookings, name='proxy_bookings'),
    path('api/book/', views.proxy_book, name='proxy_book'),
    path('api/payment/', views.proxy_payment, name='proxy_payment'),
]
