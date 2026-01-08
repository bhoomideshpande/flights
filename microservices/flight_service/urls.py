"""
Flight Service URLs
Handles: flight search, places query, flight details
"""
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/places/', views.api_places, name='api_places'),
    path('api/places/search/<str:q>/', views.api_places_search, name='api_places_search'),
    path('api/flights/search/', views.api_flights_search, name='api_flights_search'),
    path('api/flights/<int:flight_id>/', views.api_flight_detail, name='api_flight_detail'),
    
    # Web endpoints (for template rendering)
    path('', views.index, name='index'),
    path('query/places/<str:q>', views.query, name='query'),
    path('search/', views.flight_search, name='flight'),
    path('review/', views.review, name='review'),
    
    # Health check
    path('health/', views.health_check, name='health'),
]
