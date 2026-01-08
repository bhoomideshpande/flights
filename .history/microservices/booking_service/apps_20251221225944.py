from django.apps import AppConfig


class BookingServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'microservices.booking_service'
    label = 'booking_service'
