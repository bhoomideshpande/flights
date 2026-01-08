"""
Shared constants for all microservices
"""

# Fee and Surcharge
FEE = 600

# Service ports
USER_SERVICE_PORT = 8001
FLIGHT_SERVICE_PORT = 8002
BOOKING_SERVICE_PORT = 8003

# Service URLs (for inter-service communication)
USER_SERVICE_URL = f"http://localhost:{USER_SERVICE_PORT}"
FLIGHT_SERVICE_URL = f"http://localhost:{FLIGHT_SERVICE_PORT}"
BOOKING_SERVICE_URL = f"http://localhost:{BOOKING_SERVICE_PORT}"
