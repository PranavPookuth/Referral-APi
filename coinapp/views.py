from datetime import datetime

import random
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import  BasicAuthentication

from rest_framework.response import Response
from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics,status
from rest_framework.views import APIView
from django.core.mail import send_mail

# Create your views here.

class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        mobile_number = request.data.get('mobile_number')

        try:
            user = User.objects.get(email=email, mobile_number=mobile_number)

            if user.is_verified:
                return Response({'error': 'User with this email and mobile number is already verified.'},
                                status=status.HTTP_400_BAD_REQUEST)

            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            send_mail(
                'OTP Verification',
                f'Your new OTP is {otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )

            return Response({'message': 'A new OTP has been sent to your email. Please verify your OTP.'},
                            status=status.HTTP_200_OK)

        except User.DoesNotExist:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()

                # Fetch the referral information if exists
                referred_by_username = None
                referred_by_name = None
                if user.referred_by:
                    referred_by_username = user.referred_by.username
                    referred_by_name = user.referred_by.name  # Get referred user's name

                otp = random.randint(100000, 999999)
                user.otp = otp
                user.save()

                send_mail(
                    'OTP Verification',
                    f'Your OTP is {otp}',
                    'praveencodeedex@gmail.com',
                    [user.email]
                )

                return Response({
                    'message': 'OTP Sent successfully! Please verify your OTP.',
                    'referred_by_username': referred_by_username,
                    'referred_by_name': referred_by_name
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['otp']
            try:
                user = User.objects.get(email=email)
                if user.otp == otp:
                    user.is_active = True
                    user.is_verified = True
                    user.otp = None
                    user.save()
                    return Response({'message': 'Email verified successfully! You can now log in.'},
                                    status=status.HTTP_200_OK)
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({'message': 'Logged in successfully!', 'user_id': user.id,'status':True}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        response=Response()
        response.delete_cookie('jwt')
        response.data={
            'message':'logout successful',
            'status':'True'
        }
        return response


class Usercreateview(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer

class Userdetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CoinPurchaseView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        number_of_coins = request.data.get("number_of_coins", 1)

        # Check if the user has a referring user
        referred_by = user.referred_by if hasattr(user, 'referred_by') else None

        points_awarded_to_referrer = 0
        referred_user_first_purchase = False

        # Award points to the referrer if applicable
        if referred_by:
            referred_by.points = int(referred_by.points)

            # Perform the addition after both are integers
            referred_by.points += points_awarded_to_referrer
            referred_by.save()

        # Create the coin purchase record
        coin_purchase = CoinPurchase.objects.create(
            user=user,
            referred_by=referred_by,
            number_of_coins=number_of_coins,
            points_awarded_to_referrer=points_awarded_to_referrer
        )

        # Check if it's the referred user's first purchase and award points to them
        if not user.points:
            referred_user_first_purchase = True
            user.points = int(user.points)  # Force to integer before adding points
            user.points += 10  # Award 10 points (or any other number) to the referred user on first purchase
            user.save()

        # Prepare the response
        return Response({
            "message": f"{number_of_coins} coin(s) purchased successfully!",
            "points_awarded_to_referrer": points_awarded_to_referrer,
            "total_points_for_referrer": referred_by.points if referred_by else 0,
            "referred_user_first_purchase": referred_user_first_purchase,
        }, status=status.HTTP_201_CREATED)

class UserPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "user_email": user.email,
            "points_balance": user.points
        })

class HotelListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class HotelDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer


class HotelBookingView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def post(self, request):
        serializer = HotelBookingSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['name']
            hotel = serializer.validated_data['hotel']
            number_of_rooms = serializer.validated_data['number_of_rooms']
            points_used = serializer.validated_data['points_used']

            # Check if enough rooms are available for the requested date
            check_in_date = request.data.get('check_in_date')  # Assuming this is passed in the request
            if check_in_date:
                check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d").date()
                available_rooms = hotel.available_on_date(check_in_date)
                if available_rooms < number_of_rooms:
                    return Response({"error": "Not enough rooms available for the selected date."},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Reduce the user's points based on the points used
            user.points -= points_used
            user.save()

            # Create the hotel booking (this will also calculate and apply the discount)
            booking = serializer.save()

            # Apply the discount based on points used
            booking.apply_discount()

            # Reduce the available rooms for the hotel
            hotel.available_rooms -= number_of_rooms  # Decrease by the number of rooms booked
            hotel.save()

            # Return a success response with the final price, discount, and booking date
            return Response({
                "message": "Hotel booking successful!",
                "total_price": str(booking.total_price),  # Final price after discount
                "discount_applied": str(booking.discount_applied),  # Discount applied
                "points_used": booking.points_used,
                "remaining_points": user.points,
                "booking_date": booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),  # Show booking date and time
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HotelSearchView(APIView):
    def get(self, request):
        location = request.query_params.get('location', None)
        check_in_date = request.query_params.get('check_in_date', None)
        max_price = request.query_params.get('max_price', None)
        available_rooms = None

        if not check_in_date:
            return Response({"error": "check_in_date is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the check_in_date using datetime.strptime
        try:
            check_in_date = datetime.strptime(check_in_date, "%m/%d/%Y").date()
        except ValueError:
            return Response({"error": "Invalid date format, expected MM/DD/YYYY"}, status=status.HTTP_400_BAD_REQUEST)

        hotels = Hotel.objects.all()

        if location:
            hotels = hotels.filter(location__icontains=location)

        if max_price:
            hotels = hotels.filter(price_per__lte=max_price)

        available_hotels = []

        for hotel in hotels:
            # Check room availability for the given date
            available_rooms = hotel.available_on_date(check_in_date)

            if available_rooms > 0:
                available_hotels.append({
                    'hotel_name': hotel.name,
                    'location': hotel.location,
                    'price_per_night': str(hotel.price_per),
                    'available_rooms': available_rooms,
                    'check_in_date': check_in_date
                })

        return Response(available_hotels, status=status.HTTP_200_OK)
