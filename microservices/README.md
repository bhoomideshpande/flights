# Flight Ticket Booking - Microservices Architecture

This project has been refactored from a monolithic Django application into **3 microservices** that share the same SQLite database.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (8000)                       │
│                    Routes requests to services                  │
└─────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ User Service  │    │ Flight Service│    │Booking Service│
│   (8001)      │    │    (8002)     │    │    (8003)     │
├───────────────┤    ├───────────────┤    ├───────────────┤
│ - Login       │    │ - Search      │    │ - Book Ticket │
│ - Register    │    │   Flights     │    │ - Payment     │
│ - Logout      │    │ - Places      │    │ - Bookings    │
│ - User Info   │    │   Query       │    │ - Cancel      │
│               │    │ - Flight      │    │   Ticket      │
│               │    │   Details     │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                    ┌───────────────────┐
                    │  Shared Database  │
                    │   (db.sqlite3)    │
                    └───────────────────┘
```

## Services

### 1. User Service (Port 8001)
Handles user authentication and management.

**Endpoints:**
- `POST /api/login/` - User login
- `POST /api/register/` - User registration
- `POST /api/logout/` - User logout
- `GET /api/user/` - Get user info (authenticated)
- `POST /api/validate-token/` - Validate auth token
- `GET /health/` - Health check

### 2. Flight Service (Port 8002)
Handles flight search and place queries.

**Endpoints:**
- `GET /api/places/` - Get all airports/places
- `GET /api/places/search/<query>/` - Search places
- `GET/POST /api/flights/search/` - Search flights
- `GET /api/flights/<id>/` - Get flight details
- `GET /health/` - Health check

**Search Parameters:**
- `origin` - Origin airport code (e.g., "DEL")
- `destination` - Destination airport code (e.g., "BOM")
- `depart_date` - Departure date (YYYY-MM-DD)
- `seat_class` - economy/business/first
- `trip_type` - 1 (one-way) or 2 (round-trip)
- `return_date` - Return date for round trips

### 3. Booking Service (Port 8003)
Handles ticket booking, payment, and booking management.

**Endpoints:**
- `POST /api/book/` - Create a booking (authenticated)
- `POST /api/payment/` - Process payment (authenticated)
- `GET /api/bookings/` - Get user's bookings (authenticated)
- `GET /api/ticket/<ref>/` - Get ticket details
- `POST /api/ticket/<ref>/cancel/` - Cancel ticket (authenticated)
- `GET /health/` - Health check

## Quick Start

### Option 1: Run with Python (Development)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install djangorestframework django-cors-headers requests
   ```

2. **Start all services:**
   
   **Windows (PowerShell):**
   ```powershell
   cd microservices
   .\start_all_services.ps1
   ```
   
   **Linux/Mac:**
   ```bash
   cd microservices
   chmod +x start_all_services.sh
   ./start_all_services.sh
   ```

3. **Or start each service individually:**
   ```bash
   # Terminal 1 - User Service
   python -m django runserver 8001 --settings=microservices.user_service.settings
   
   # Terminal 2 - Flight Service
   python -m django runserver 8002 --settings=microservices.flight_service.settings
   
   # Terminal 3 - Booking Service
   python -m django runserver 8003 --settings=microservices.booking_service.settings
   
   # Terminal 4 - API Gateway
   python -m django runserver 8000 --settings=microservices.api_gateway.settings
   ```

### Option 2: Run with Docker

```bash
cd microservices
docker-compose up --build
```

## Database

All microservices share the same SQLite database (`db.sqlite3`) located in the project root. This ensures data consistency across services.

**Shared Tables:**
- `flight_user` - User accounts
- `flight_place` - Airports/Places
- `flight_week` - Week days
- `flight_flight` - Flight information
- `flight_passenger` - Passenger details
- `flight_ticket` - Bookings/Tickets

## API Usage Examples

### Login
```bash
curl -X POST http://localhost:8001/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

### Search Flights
```bash
curl "http://localhost:8002/api/flights/search/?origin=DEL&destination=BOM&depart_date=2025-01-15&seat_class=economy"
```

### Create Booking
```bash
curl -X POST http://localhost:8003/api/book/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "flight_id": 1,
    "flight_date": "15-01-2025",
    "seat_class": "economy",
    "passengers": [{"first_name": "John", "last_name": "Doe", "gender": "male"}],
    "mobile": "9876543210",
    "email": "john@example.com"
  }'
```

### Health Check
```bash
curl http://localhost:8000/health/
```

## Project Structure

```
microservices/
├── shared/
│   ├── __init__.py
│   ├── models.py          # Shared model definitions
│   ├── constants.py       # Shared constants
│   └── database.py        # Database configuration
├── user_service/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── apps.py
│   ├── wsgi.py
│   └── manage.py
├── flight_service/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── apps.py
│   ├── wsgi.py
│   └── manage.py
├── booking_service/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── apps.py
│   ├── wsgi.py
│   └── manage.py
├── api_gateway/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── wsgi.py
│   └── manage.py
├── docker-compose.yml
├── Dockerfile.user
├── Dockerfile.flight
├── Dockerfile.booking
├── Dockerfile.gateway
├── start_all_services.ps1
├── start_all_services.sh
└── README.md
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 8000 | Routes requests to services |
| User Service | 8001 | Authentication |
| Flight Service | 8002 | Flight search |
| Booking Service | 8003 | Ticket booking |

## Benefits of Microservices

1. **Independent Scaling** - Each service can be scaled independently
2. **Technology Flexibility** - Services can use different technologies
3. **Fault Isolation** - Failure in one service doesn't affect others
4. **Easier Maintenance** - Smaller codebases are easier to maintain
5. **Team Independence** - Different teams can work on different services

## Original Monolithic App

The original monolithic application is still available and can be run with:
```bash
python manage.py runserver
```

This runs on port 8000 by default.
