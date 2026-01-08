"""
Flight Service Views
Handles flight search and queries
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import math

from flight.models import Place, Week, Flight
from flight.constant import FEE


# ==================== API ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_places(request):
    """API endpoint to get all places/airports"""
    places = Place.objects.all()
    return Response({
        'success': True,
        'places': [{
            'id': place.id,
            'city': place.city,
            'airport': place.airport,
            'code': place.code,
            'country': place.country
        } for place in places]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_places_search(request, q):
    """API endpoint to search places/airports"""
    places = Place.objects.all()
    filters = []
    q = q.lower()
    
    for place in places:
        if (q in place.city.lower()) or (q in place.airport.lower()) or \
           (q in place.code.lower()) or (q in place.country.lower()):
            filters.append({
                'id': place.id,
                'city': place.city,
                'airport': place.airport,
                'code': place.code,
                'country': place.country
            })
    
    return Response({
        'success': True,
        'places': filters
    })


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_flights_search(request):
    """API endpoint to search for flights"""
    try:
        # Get parameters from GET or POST
        if request.method == 'POST':
            data = request.data
        else:
            data = request.GET
        
        origin_code = data.get('origin')
        destination_code = data.get('destination')
        depart_date_str = data.get('depart_date')
        seat_class = data.get('seat_class', 'economy').lower()
        trip_type = data.get('trip_type', '1')
        return_date_str = data.get('return_date')
        
        if not all([origin_code, destination_code, depart_date_str]):
            return Response({
                'success': False,
                'error': 'Origin, destination, and departure date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        depart_date = datetime.strptime(depart_date_str, "%Y-%m-%d")
        flightday = Week.objects.get(number=depart_date.weekday())
        origin = Place.objects.get(code=origin_code.upper())
        destination = Place.objects.get(code=destination_code.upper())
        
        # Get outbound flights
        if seat_class == 'economy':
            flights = Flight.objects.filter(
                depart_day=flightday, origin=origin, destination=destination
            ).exclude(economy_fare=0).order_by('economy_fare')
        elif seat_class == 'business':
            flights = Flight.objects.filter(
                depart_day=flightday, origin=origin, destination=destination
            ).exclude(business_fare=0).order_by('business_fare')
        else:  # first class
            flights = Flight.objects.filter(
                depart_day=flightday, origin=origin, destination=destination
            ).exclude(first_fare=0).order_by('first_fare')
        
        outbound_flights = []
        for f in flights:
            fare = f.economy_fare if seat_class == 'economy' else \
                   (f.business_fare if seat_class == 'business' else f.first_fare)
            outbound_flights.append({
                'id': f.id,
                'origin': {'city': f.origin.city, 'code': f.origin.code, 'country': f.origin.country},
                'destination': {'city': f.destination.city, 'code': f.destination.code, 'country': f.destination.country},
                'depart_time': f.depart_time.strftime('%H:%M'),
                'arrival_time': f.arrival_time.strftime('%H:%M'),
                'duration': str(f.duration),
                'airline': f.airline,
                'plane': f.plane,
                'fare': fare
            })
        
        response_data = {
            'success': True,
            'outbound_flights': outbound_flights,
            'origin': {'city': origin.city, 'code': origin.code},
            'destination': {'city': destination.city, 'code': destination.code},
            'depart_date': depart_date_str,
            'seat_class': seat_class
        }
        
        # Handle round trip
        if trip_type == '2' and return_date_str:
            return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
            flightday2 = Week.objects.get(number=return_date.weekday())
            
            if seat_class == 'economy':
                flights2 = Flight.objects.filter(
                    depart_day=flightday2, origin=destination, destination=origin
                ).exclude(economy_fare=0).order_by('economy_fare')
            elif seat_class == 'business':
                flights2 = Flight.objects.filter(
                    depart_day=flightday2, origin=destination, destination=origin
                ).exclude(business_fare=0).order_by('business_fare')
            else:
                flights2 = Flight.objects.filter(
                    depart_day=flightday2, origin=destination, destination=origin
                ).exclude(first_fare=0).order_by('first_fare')
            
            return_flights = []
            for f in flights2:
                fare = f.economy_fare if seat_class == 'economy' else \
                       (f.business_fare if seat_class == 'business' else f.first_fare)
                return_flights.append({
                    'id': f.id,
                    'origin': {'city': f.origin.city, 'code': f.origin.code, 'country': f.origin.country},
                    'destination': {'city': f.destination.city, 'code': f.destination.code, 'country': f.destination.country},
                    'depart_time': f.depart_time.strftime('%H:%M'),
                    'arrival_time': f.arrival_time.strftime('%H:%M'),
                    'duration': str(f.duration),
                    'airline': f.airline,
                    'plane': f.plane,
                    'fare': fare
                })
            
            response_data['return_flights'] = return_flights
            response_data['return_date'] = return_date_str
        
        return Response(response_data)
        
    except Place.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid origin or destination'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Week.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid date'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_flight_detail(request, flight_id):
    """API endpoint to get flight details"""
    try:
        flight = Flight.objects.get(id=flight_id)
        return Response({
            'success': True,
            'flight': {
                'id': flight.id,
                'origin': {
                    'city': flight.origin.city,
                    'airport': flight.origin.airport,
                    'code': flight.origin.code,
                    'country': flight.origin.country
                },
                'destination': {
                    'city': flight.destination.city,
                    'airport': flight.destination.airport,
                    'code': flight.destination.code,
                    'country': flight.destination.country
                },
                'depart_time': flight.depart_time.strftime('%H:%M'),
                'arrival_time': flight.arrival_time.strftime('%H:%M'),
                'duration': str(flight.duration),
                'airline': flight.airline,
                'plane': flight.plane,
                'economy_fare': flight.economy_fare,
                'business_fare': flight.business_fare,
                'first_fare': flight.first_fare
            }
        })
    except Flight.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Flight not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ==================== WEB ENDPOINTS ====================

def index(request):
    """Home page with flight search form"""
    min_date = f"{datetime.now().date().year}-{datetime.now().date().month}-{datetime.now().date().day}"
    max_date = f"{datetime.now().date().year if (datetime.now().date().month+3)<=12 else datetime.now().date().year+1}-{(datetime.now().date().month + 3) if (datetime.now().date().month+3)<=12 else (datetime.now().date().month+3-12)}-{datetime.now().date().day}"
    
    if request.method == 'POST':
        origin = request.POST.get('Origin')
        destination = request.POST.get('Destination')
        depart_date = request.POST.get('DepartDate')
        seat = request.POST.get('SeatClass')
        trip_type = request.POST.get('TripType')
        
        if trip_type == '1':
            return render(request, 'flight/index.html', {
                'origin': origin,
                'destination': destination,
                'depart_date': depart_date,
                'seat': seat.lower(),
                'trip_type': trip_type
            })
        elif trip_type == '2':
            return_date = request.POST.get('ReturnDate')
            return render(request, 'flight/index.html', {
                'min_date': min_date,
                'max_date': max_date,
                'origin': origin,
                'destination': destination,
                'depart_date': depart_date,
                'seat': seat.lower(),
                'trip_type': trip_type,
                'return_date': return_date
            })
    
    return render(request, 'flight/index.html', {
        'min_date': min_date,
        'max_date': max_date
    })


def query(request, q):
    """Search places/airports"""
    places = Place.objects.all()
    filters = []
    q = q.lower()
    
    for place in places:
        if (q in place.city.lower()) or (q in place.airport.lower()) or \
           (q in place.code.lower()) or (q in place.country.lower()):
            filters.append(place)
    
    return JsonResponse([{
        'code': place.code,
        'city': place.city,
        'country': place.country
    } for place in filters], safe=False)


@csrf_exempt
def flight_search(request):
    """Search for flights"""
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType')
    departdate = request.GET.get('DepartDate')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d")
    return_date = None
    seat = request.GET.get('SeatClass')
    
    flightday = Week.objects.get(number=depart_date.weekday())
    destination = Place.objects.get(code=d_place.upper())
    origin = Place.objects.get(code=o_place.upper())
    
    if trip_type == '2':
        returndate = request.GET.get('ReturnDate')
        return_date = datetime.strptime(returndate, "%Y-%m-%d")
        flightday2 = Week.objects.get(number=return_date.weekday())
        origin2 = Place.objects.get(code=d_place.upper())
        destination2 = Place.objects.get(code=o_place.upper())
    
    if seat == 'economy':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(economy_fare=0).order_by('economy_fare')
        try:
            max_price = flights.last().economy_fare
            min_price = flights.first().economy_fare
        except:
            max_price, min_price = 0, 0
        
        if trip_type == '2':
            flights2 = Flight.objects.filter(depart_day=flightday2, origin=origin2, destination=destination2).exclude(economy_fare=0).order_by('economy_fare')
            try:
                max_price2 = flights2.last().economy_fare
                min_price2 = flights2.first().economy_fare
            except:
                max_price2, min_price2 = 0, 0
    
    elif seat == 'business':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(business_fare=0).order_by('business_fare')
        try:
            max_price = flights.last().business_fare
            min_price = flights.first().business_fare
        except:
            max_price, min_price = 0, 0
        
        if trip_type == '2':
            flights2 = Flight.objects.filter(depart_day=flightday2, origin=origin2, destination=destination2).exclude(business_fare=0).order_by('business_fare')
            try:
                max_price2 = flights2.last().business_fare
                min_price2 = flights2.first().business_fare
            except:
                max_price2, min_price2 = 0, 0
    
    elif seat == 'first':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(first_fare=0).order_by('first_fare')
        try:
            max_price = flights.last().first_fare
            min_price = flights.first().first_fare
        except:
            max_price, min_price = 0, 0
        
        if trip_type == '2':
            flights2 = Flight.objects.filter(depart_day=flightday2, origin=origin2, destination=destination2).exclude(first_fare=0).order_by('first_fare')
            try:
                max_price2 = flights2.last().first_fare
                min_price2 = flights2.first().first_fare
            except:
                max_price2, min_price2 = 0, 0
    
    if trip_type == '2':
        return render(request, "flight/search.html", {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'flights2': flights2,
            'origin2': origin2,
            'destination2': destination2,
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(max_price/100)*100,
            'min_price': math.floor(min_price/100)*100,
            'max_price2': math.ceil(max_price2/100)*100,
            'min_price2': math.floor(min_price2/100)*100
        })
    
    return render(request, "flight/search.html", {
        'flights': flights,
        'origin': origin,
        'destination': destination,
        'seat': seat.capitalize(),
        'trip_type': trip_type,
        'depart_date': depart_date,
        'return_date': return_date,
        'max_price': math.ceil(max_price/100)*100,
        'min_price': math.floor(min_price/100)*100
    })


def review(request):
    """Review selected flight before booking"""
    flight_1 = request.GET.get('flight1Id')
    date1 = request.GET.get('flight1Date')
    seat = request.GET.get('seatClass')
    round_trip = False
    
    if request.GET.get('flight2Id'):
        round_trip = True
    
    flight1 = Flight.objects.get(id=flight_1)
    flight1ddate = datetime(
        int(date1.split('-')[2]), int(date1.split('-')[1]), int(date1.split('-')[0]),
        flight1.depart_time.hour, flight1.depart_time.minute
    )
    flight1adate = flight1ddate + flight1.duration
    
    flight2 = None
    flight2ddate = None
    flight2adate = None
    
    if round_trip:
        flight_2 = request.GET.get('flight2Id')
        date2 = request.GET.get('flight2Date')
        flight2 = Flight.objects.get(id=flight_2)
        flight2ddate = datetime(
            int(date2.split('-')[2]), int(date2.split('-')[1]), int(date2.split('-')[0]),
            flight2.depart_time.hour, flight2.depart_time.minute
        )
        flight2adate = flight2ddate + flight2.duration
        
        return render(request, "flight/book.html", {
            'flight1': flight1,
            'flight2': flight2,
            "flight1ddate": flight1ddate,
            "flight1adate": flight1adate,
            "flight2ddate": flight2ddate,
            "flight2adate": flight2adate,
            "seat": seat,
            "fee": FEE
        })
    
    return render(request, "flight/book.html", {
        'flight1': flight1,
        "flight1ddate": flight1ddate,
        "flight1adate": flight1adate,
        "seat": seat,
        "fee": FEE
    })


# ==================== HEALTH CHECK ====================

def health_check(request):
    """Health check endpoint for the service"""
    return JsonResponse({
        'service': 'flight-service',
        'status': 'healthy',
        'port': 8002
    })
