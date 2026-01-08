#!/bin/bash

# Bash script to start all microservices
# Run this script from the project root directory

echo "========================================"
echo "  Flight Ticket Booking Microservices  "
echo "========================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Activate virtual environment if exists
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Function to start a service
start_service() {
    SERVICE_NAME=$1
    PORT=$2
    SETTINGS_MODULE=$3
    
    echo "Starting $SERVICE_NAME on port $PORT..."
    cd "$PROJECT_ROOT"
    DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE python -m django runserver $PORT --settings=$SETTINGS_MODULE &
}

echo ""
echo "Starting Microservices..."
echo ""

# Start all services
start_service "User Service" "8001" "microservices.user_service.settings"
sleep 2

start_service "Flight Service" "8002" "microservices.flight_service.settings"
sleep 2

start_service "Booking Service" "8003" "microservices.booking_service.settings"
sleep 2

start_service "API Gateway" "8000" "microservices.api_gateway.settings"

echo ""
echo "========================================"
echo "  All Services Started!                "
echo "========================================"
echo ""
echo "Service URLs:"
echo "  API Gateway:     http://localhost:8000"
echo "  User Service:    http://localhost:8001"
echo "  Flight Service:  http://localhost:8002"
echo "  Booking Service: http://localhost:8003"
echo ""
echo "Health Check: http://localhost:8000/health/"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait
