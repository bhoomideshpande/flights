from django.apps import AppConfig


class FlightServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'microservices.flight_service'
    label = 'flight_service'
