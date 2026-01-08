"""
Booking Service Views
Handles ticket booking, payment, and bookings management
"""
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import secrets
import json

from flight.models import User, Flight, Passenger, Ticket
from flight.constant import FEE


def create_ticket(user, passengers, passengers_count, flight, flight_date, flight_class, coupon, countrycode, email, mobile):
    """Helper function to create a ticket"""
    ticket = Ticket.objects.create(
        user=user,
        ref_no=secrets.token_hex(3).upper(),
        status='PENDING'
    )
    
    for passenger in passengers:
        ticket.passengers.add(passenger)
    
    ticket.flight = flight
    ticket.flight_ddate = datetime(
        int(flight_date.split('-')[2]),
        int(flight_date.split('-')[1]),
        int(flight_date.split('-')[0])
    )
    
    flight_ddate = datetime(
        int(flight_date.split('-')[2]),
        int(flight_date.split('-')[1]),
        int(flight_date.split('-')[0]),
        flight.depart_time.hour,
        flight.depart_time.minute
    )
    flight_adate = flight_ddate + flight.duration
    ticket.flight_adate = datetime(flight_adate.year, flight_adate.month, flight_adate.day)
    
    fare = 0.0
    if flight_class.lower() == 'first':
        ticket.flight_fare = flight.first_fare * int(passengers_count)
        fare = flight.first_fare * int(passengers_count)
    elif flight_class.lower() == 'business':
        ticket.flight_fare = flight.business_fare * int(passengers_count)
        fare = flight.business_fare * int(passengers_count)
    else:
        ticket.flight_fare = flight.economy_fare * int(passengers_count)
        fare = flight.economy_fare * int(passengers_count)
    
    ticket.other_charges = FEE
    if coupon:
        ticket.coupon_used = coupon
    ticket.total_fare = fare + FEE
    ticket.seat_class = flight_class.lower()
    ticket.mobile = f'+{countrycode} {mobile}'
    ticket.email = email
    ticket.save()
    
    return ticket


# ==================== API ENDPOINTS ====================

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_book(request):
    """API endpoint to create a booking"""
    try:
        data = request.data
        
        flight_id = data.get('flight_id')
        flight_date = data.get('flight_date')
        seat_class = data.get('seat_class')
        passengers_data = data.get('passengers', [])
        mobile = data.get('mobile')
        country_code = data.get('country_code', '91')
        email = data.get('email')
        coupon = data.get('coupon', '')
        
        # Return flight (optional)
        flight2_id = data.get('flight2_id')
        flight2_date = data.get('flight2_date')
        
        if not all([flight_id, flight_date, seat_class, passengers_data, mobile, email]):
            return Response({
                'success': False,
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        flight = Flight.objects.get(id=flight_id)
        
        # Create passengers
        passengers = []
        for p in passengers_data:
            passenger = Passenger.objects.create(
                first_name=p.get('first_name', ''),
                last_name=p.get('last_name', ''),
                gender=p.get('gender', '').lower()
            )
            passengers.append(passenger)
        
        # Create ticket
        ticket1 = create_ticket(
            request.user, passengers, len(passengers),
            flight, flight_date, seat_class, coupon,
            country_code, email, mobile
        )
        
        response_data = {
            'success': True,
            'ticket': {
                'id': ticket1.id,
                'ref_no': ticket1.ref_no,
                'total_fare': ticket1.total_fare,
                'status': ticket1.status
            }
        }
        
        # Handle return flight
        if flight2_id and flight2_date:
            flight2 = Flight.objects.get(id=flight2_id)
            ticket2 = create_ticket(
                request.user, passengers, len(passengers),
                flight2, flight2_date, seat_class, coupon,
                country_code, email, mobile
            )
            response_data['ticket2'] = {
                'id': ticket2.id,
                'ref_no': ticket2.ref_no,
                'total_fare': ticket2.total_fare,
                'status': ticket2.status
            }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Flight.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Flight not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_payment(request):
    """API endpoint to process payment"""
    try:
        data = request.data
        
        ticket_id = data.get('ticket_id')
        ticket2_id = data.get('ticket2_id')
        card_number = data.get('card_number')
        card_holder = data.get('card_holder')
        exp_month = data.get('exp_month')
        exp_year = data.get('exp_year')
        cvv = data.get('cvv')
        
        if not all([ticket_id, card_number, card_holder, exp_month, exp_year, cvv]):
            return Response({
                'success': False,
                'error': 'Missing payment details'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ticket = Ticket.objects.get(id=ticket_id)
        
        if ticket.user != request.user:
            return Response({
                'success': False,
                'error': 'Unauthorized'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Process payment (simulated)
        ticket.status = 'CONFIRMED'
        ticket.booking_date = datetime.now()
        ticket.save()
        
        response_data = {
            'success': True,
            'message': 'Payment successful',
            'ticket': {
                'ref_no': ticket.ref_no,
                'status': ticket.status
            }
        }
        
        if ticket2_id:
            ticket2 = Ticket.objects.get(id=ticket2_id)
            ticket2.status = 'CONFIRMED'
            ticket2.booking_date = datetime.now()
            ticket2.save()
            response_data['ticket2'] = {
                'ref_no': ticket2.ref_no,
                'status': ticket2.status
            }
        
        return Response(response_data)
        
    except Ticket.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Ticket not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_bookings(request):
    """API endpoint to get user's bookings"""
    tickets = Ticket.objects.filter(user=request.user).order_by('-booking_date')
    
    bookings = []
    for ticket in tickets:
        bookings.append({
            'id': ticket.id,
            'ref_no': ticket.ref_no,
            'flight': {
                'origin': ticket.flight.origin.code if ticket.flight else None,
                'destination': ticket.flight.destination.code if ticket.flight else None,
                'airline': ticket.flight.airline if ticket.flight else None
            },
            'flight_date': ticket.flight_ddate,
            'seat_class': ticket.seat_class,
            'total_fare': ticket.total_fare,
            'status': ticket.status,
            'booking_date': ticket.booking_date
        })
    
    return Response({
        'success': True,
        'bookings': bookings
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_ticket_detail(request, ref):
    """API endpoint to get ticket details"""
    try:
        ticket = Ticket.objects.get(ref_no=ref)
        return Response({
            'success': True,
            'ticket': {
                'ref_no': ticket.ref_no,
                'origin': ticket.flight.origin.code if ticket.flight else None,
                'destination': ticket.flight.destination.code if ticket.flight else None,
                'flight_date': ticket.flight_ddate,
                'status': ticket.status,
                'seat_class': ticket.seat_class,
                'total_fare': ticket.total_fare
            }
        })
    except Ticket.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Ticket not found'
        }, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_cancel_ticket(request, ref):
    """API endpoint to cancel a ticket"""
    try:
        ticket = Ticket.objects.get(ref_no=ref)
        
        if ticket.user != request.user:
            return Response({
                'success': False,
                'error': 'Unauthorized'
            }, status=status.HTTP_403_FORBIDDEN)
        
        ticket.status = 'CANCELLED'
        ticket.save()
        
        return Response({
            'success': True,
            'message': 'Ticket cancelled successfully'
        })
        
    except Ticket.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Ticket not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ==================== WEB ENDPOINTS ====================

def book(request):
    """Web endpoint for booking"""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login/')
        
        flight_1 = request.POST.get('flight1')
        flight_1date = request.POST.get('flight1Date')
        flight_1class = request.POST.get('flight1Class')
        f2 = False
        
        if request.POST.get('flight2'):
            flight_2 = request.POST.get('flight2')
            flight_2date = request.POST.get('flight2Date')
            flight_2class = request.POST.get('flight2Class')
            f2 = True
        
        countrycode = request.POST['countryCode']
        mobile = request.POST['mobile']
        email = request.POST['email']
        flight1 = Flight.objects.get(id=flight_1)
        
        if f2:
            flight2 = Flight.objects.get(id=flight_2)
        
        passengerscount = request.POST['passengersCount']
        passengers = []
        
        for i in range(1, int(passengerscount) + 1):
            fname = request.POST[f'passenger{i}FName']
            lname = request.POST[f'passenger{i}LName']
            gender = request.POST[f'passenger{i}Gender']
            passengers.append(Passenger.objects.create(
                first_name=fname, last_name=lname, gender=gender.lower()
            ))
        
        coupon = request.POST.get('coupon')
        
        try:
            ticket1 = create_ticket(
                request.user, passengers, passengerscount,
                flight1, flight_1date, flight_1class, coupon,
                countrycode, email, mobile
            )
            
            if f2:
                ticket2 = create_ticket(
                    request.user, passengers, passengerscount,
                    flight2, flight_2date, flight_2class, coupon,
                    countrycode, email, mobile
                )
            
            if flight_1class == 'Economy':
                if f2:
                    fare = (flight1.economy_fare * int(passengerscount)) + (flight2.economy_fare * int(passengerscount))
                else:
                    fare = flight1.economy_fare * int(passengerscount)
            elif flight_1class == 'Business':
                if f2:
                    fare = (flight1.business_fare * int(passengerscount)) + (flight2.business_fare * int(passengerscount))
                else:
                    fare = flight1.business_fare * int(passengerscount)
            elif flight_1class == 'First':
                if f2:
                    fare = (flight1.first_fare * int(passengerscount)) + (flight2.first_fare * int(passengerscount))
                else:
                    fare = flight1.first_fare * int(passengerscount)
            
            if f2:
                return render(request, "flight/payment.html", {
                    'fare': fare + FEE,
                    'ticket': ticket1.id,
                    'ticket2': ticket2.id
                })
            
            return render(request, "flight/payment.html", {
                'fare': fare + FEE,
                'ticket': ticket1.id
            })
            
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be POST.")


def payment(request):
    """Web endpoint for payment processing"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/user/login/')
    
    if request.method == 'POST':
        ticket_id = request.POST['ticket']
        t2 = False
        
        if request.POST.get('ticket2'):
            ticket2_id = request.POST['ticket2']
            t2 = True
        
        fare = request.POST.get('fare')
        card_number = request.POST['cardNumber']
        card_holder_name = request.POST['cardHolderName']
        exp_month = request.POST['expMonth']
        exp_year = request.POST['expYear']
        cvv = request.POST['cvv']
        
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.status = 'CONFIRMED'
            ticket.booking_date = datetime.now()
            ticket.save()
            
            if t2:
                ticket2 = Ticket.objects.get(id=ticket2_id)
                ticket2.status = 'CONFIRMED'
                ticket2.save()
                return render(request, 'flight/payment_process.html', {
                    'ticket1': ticket,
                    'ticket2': ticket2
                })
            
            return render(request, 'flight/payment_process.html', {
                'ticket1': ticket,
                'ticket2': ""
            })
            
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be POST.")


def ticket_data(request, ref):
    """Web endpoint for ticket data"""
    ticket = Ticket.objects.get(ref_no=ref)
    return JsonResponse({
        'ref': ticket.ref_no,
        'from': ticket.flight.origin.code if ticket.flight else None,
        'to': ticket.flight.destination.code if ticket.flight else None,
        'flight_date': ticket.flight_ddate,
        'status': ticket.status
    })


def bookings(request):
    """Web endpoint for user's bookings"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/user/login/')
    
    tickets = Ticket.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'flight/bookings.html', {
        'page': 'bookings',
        'tickets': tickets
    })


@csrf_exempt
def cancel_ticket(request):
    """Web endpoint to cancel ticket"""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse("User unauthorised")
        
        ref = request.POST['ref']
        try:
            ticket = Ticket.objects.get(ref_no=ref)
            if ticket.user == request.user:
                ticket.status = 'CANCELLED'
                ticket.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({
                    'success': False,
                    'error': "User unauthorised"
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    else:
        return HttpResponse("Method must be POST.")


def resume_booking(request):
    """Web endpoint to resume pending booking"""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/user/login/')
        
        ref = request.POST['ref']
        ticket = Ticket.objects.get(ref_no=ref)
        
        if ticket.user == request.user:
            return render(request, "flight/payment.html", {
                'fare': ticket.total_fare,
                'ticket': ticket.id
            })
        else:
            return HttpResponse("User unauthorised")
    else:
        return HttpResponse("Method must be POST.")


# ==================== HEALTH CHECK ====================

def health_check(request):
    """Health check endpoint for the service"""
    return JsonResponse({
        'service': 'booking-service',
        'status': 'healthy',
        'port': 8003
    })
