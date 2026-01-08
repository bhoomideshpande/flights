"""
API Gateway Views
Proxies requests to appropriate microservices
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# Service URLs
USER_SERVICE_URL = "http://localhost:8001"
FLIGHT_SERVICE_URL = "http://localhost:8002"
BOOKING_SERVICE_URL = "http://localhost:8003"


def index(request):
    """API Gateway home page"""
    return JsonResponse({
        'service': 'API Gateway',
        'version': '1.0',
        'endpoints': {
            'user_service': f'{USER_SERVICE_URL}',
            'flight_service': f'{FLIGHT_SERVICE_URL}',
            'booking_service': f'{BOOKING_SERVICE_URL}'
        },
        'routes': {
            '/api/user/*': 'User Service (Authentication)',
            '/api/flights/*': 'Flight Service (Search)',
            '/api/places/*': 'Flight Service (Places)',
            '/api/bookings/*': 'Booking Service',
            '/api/book/*': 'Booking Service',
            '/api/payment/*': 'Booking Service'
        }
    })


def health_check(request):
    """Health check for all services"""
    services = {
        'api_gateway': {'status': 'healthy', 'port': 8000},
        'user_service': check_service_health(USER_SERVICE_URL),
        'flight_service': check_service_health(FLIGHT_SERVICE_URL),
        'booking_service': check_service_health(BOOKING_SERVICE_URL)
    }
    
    all_healthy = all(s.get('status') == 'healthy' for s in services.values())
    
    return JsonResponse({
        'overall_status': 'healthy' if all_healthy else 'degraded',
        'services': services
    })


def check_service_health(url):
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}/health/", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {'status': 'unhealthy', 'error': f'Status code: {response.status_code}'}
    except requests.exceptions.ConnectionError:
        return {'status': 'unreachable', 'error': 'Connection refused'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def services_status(request):
    """Get status of all microservices"""
    return JsonResponse({
        'services': [
            {
                'name': 'User Service',
                'url': USER_SERVICE_URL,
                'port': 8001,
                'endpoints': ['/api/login/', '/api/register/', '/api/logout/', '/api/user/']
            },
            {
                'name': 'Flight Service',
                'url': FLIGHT_SERVICE_URL,
                'port': 8002,
                'endpoints': ['/api/places/', '/api/flights/search/', '/api/flights/<id>/']
            },
            {
                'name': 'Booking Service',
                'url': BOOKING_SERVICE_URL,
                'port': 8003,
                'endpoints': ['/api/book/', '/api/payment/', '/api/bookings/', '/api/ticket/<ref>/']
            }
        ]
    })


# ==================== PROXY FUNCTIONS ====================

def proxy_request(service_url, path, request):
    """Generic proxy function"""
    try:
        url = f"{service_url}{path}"
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
        
        if request.method == 'GET':
            response = requests.get(url, params=request.GET, headers=headers, timeout=30)
        elif request.method == 'POST':
            try:
                data = json.loads(request.body) if request.body else {}
            except:
                data = dict(request.POST)
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        return JsonResponse(response.json(), status=response.status_code)
        
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'error': 'Service unavailable',
            'service_url': service_url
        }, status=503)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def proxy_user_login(request):
    return proxy_request(USER_SERVICE_URL, '/api/login/', request)


@csrf_exempt
def proxy_user_register(request):
    return proxy_request(USER_SERVICE_URL, '/api/register/', request)


@csrf_exempt
def proxy_user_logout(request):
    return proxy_request(USER_SERVICE_URL, '/api/logout/', request)


def proxy_flight_search(request):
    return proxy_request(FLIGHT_SERVICE_URL, '/api/flights/search/', request)


def proxy_places(request):
    return proxy_request(FLIGHT_SERVICE_URL, '/api/places/', request)


def proxy_places_search(request, q):
    return proxy_request(FLIGHT_SERVICE_URL, f'/api/places/search/{q}/', request)


def proxy_bookings(request):
    return proxy_request(BOOKING_SERVICE_URL, '/api/bookings/', request)


@csrf_exempt
def proxy_book(request):
    return proxy_request(BOOKING_SERVICE_URL, '/api/book/', request)


@csrf_exempt
def proxy_payment(request):
    return proxy_request(BOOKING_SERVICE_URL, '/api/payment/', request)
