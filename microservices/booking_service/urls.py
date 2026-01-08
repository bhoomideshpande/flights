"""
Booking Service URLs
Handles: booking, payment, tickets, bookings list
"""
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/book/', views.api_book, name='api_book'),
    path('api/payment/', views.api_payment, name='api_payment'),
    path('api/bookings/', views.api_bookings, name='api_bookings'),
    path('api/ticket/<str:ref>/', views.api_ticket_detail, name='api_ticket_detail'),
    path('api/ticket/<str:ref>/cancel/', views.api_cancel_ticket, name='api_cancel_ticket'),
    
    # Web endpoints (for template rendering)
    path('book/', views.book, name='book'),
    path('payment/', views.payment, name='payment'),
    path('bookings/', views.bookings, name='bookings'),
    path('ticket/api/<str:ref>/', views.ticket_data, name='ticketdata'),
    path('ticket/cancel/', views.cancel_ticket, name='cancelticket'),
    path('ticket/resume/', views.resume_booking, name='resumebooking'),
    
    # Health check
    path('health/', views.health_check, name='health'),
]
