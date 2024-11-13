from datetime import datetime

import random
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import  BasicAuthentication

from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
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

class hotelview(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class HotelDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=pk)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HotelSerializer(hotel)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=pk)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the request data and validate it
        serializer = HotelSerializer(hotel, data=request.data, partial=True)

        if serializer.is_valid():
            # Handle room types update (if provided in the request)
            room_types_data = request.data.get('room_types', [])
            if room_types_data:
                # Clear and re-add room types if provided in the request
                hotel.room_types.clear()

                for room_data in room_types_data:
                    room_type, created = RoomType.objects.update_or_create(
                        hotel=hotel,
                        room_name=room_data['room_name'],
                        defaults={'price_per_night': room_data['price_per_night'], 'available_rooms': room_data['available_rooms']}
                    )
                    hotel.room_types.add(room_type)

            # Save the updated hotel instance
            updated_hotel = serializer.save()

            return Response(HotelSerializer(updated_hotel).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HotelBookingView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def post(self, request):
        hotel_name = request.data.get('hotel_name')
        room_type_name = request.data.get('room_type_name')
        number_of_rooms = request.data.get('number_of_rooms')
        points_used = request.data.get('points_used', 0)
        check_in_date = request.data.get('check_in_date')
        check_out_date = request.data.get('check_out_date')  # Get check-out date from request
        user = request.user  # The authenticated user

        # Validate input
        if not hotel_name or not room_type_name or not number_of_rooms or not check_in_date or not check_out_date:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert the check-in and check-out dates to datetime objects
        try:
            check_in_date = datetime.strptime(check_in_date, "%m/%d/%Y").date()
            check_out_date = datetime.strptime(check_out_date, "%m/%d/%Y").date()
        except ValueError:
            return Response({"error": "Invalid date format, expected MM/DD/YYYY"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure that check-out date is after check-in date
        if check_out_date <= check_in_date:
            return Response({"error": "Check-out date must be after check-in date."}, status=status.HTTP_400_BAD_REQUEST)

        # Look up the Hotel by name
        try:
            hotel = Hotel.objects.get(name=hotel_name)
        except Hotel.DoesNotExist:
            return Response({"error": f"Hotel with name '{hotel_name}' not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Look up the RoomType by name and filter by hotel
        try:
            room_type = RoomType.objects.get(room_name=room_type_name, hotel=hotel)
        except RoomType.DoesNotExist:
            return Response({"error": f"Room type '{room_type_name}' not found in hotel '{hotel_name}'."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the total price based on the number of nights
        total_nights = (check_out_date - check_in_date).days
        total_price = room_type.price_per_night * total_nights * number_of_rooms

        # Create the booking data
        booking_data = {
            "hotel_name": hotel_name,
            "room_type_name": room_type_name,
            "number_of_rooms": number_of_rooms,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,  # Include check-out date
            "points_used": points_used,
            "user": user.id,
            "name": user.id,
            "total_price": total_price
        }

        serializer = HotelBookingSerializer(data=booking_data, context={'request': request})

        if serializer.is_valid():
            booking = serializer.save()
            return Response(HotelBookingSerializer(booking).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class HotelSearchView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get(self, request):
        location = request.query_params.get('location', None)
        check_in_date = request.query_params.get('check_in_date', None)
        max_price = request.query_params.get('max_price', None)
        room_name = request.query_params.get('room_name', None)  # Room type to search for
        hotel_name = request.query_params.get('hotel_name', None)  # Hotel name to search for

        # Ensure check_in_date is provided
        if not check_in_date:
            return Response({"error": "check_in_date is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the check_in_date
        try:
            check_in_date = datetime.strptime(check_in_date, "%m/%d/%Y").date()
        except ValueError:
            return Response({"error": "Invalid date format, expected MM/DD/YYYY"}, status=status.HTTP_400_BAD_REQUEST)

        # Start filtering hotels
        hotels = Hotel.objects.all()

        if hotel_name:
            hotels = hotels.filter(name__icontains=hotel_name)

        if location:
            hotels = hotels.filter(location__icontains=location)

        if max_price:
            hotels = hotels.filter(price_per__lte=max_price)

        available_hotels = []

        for hotel in hotels:
            # Check availability of the specific room type for the given date
            available_rooms = hotel.available_on_date(check_in_date, room_type_name=room_name)

            if available_rooms > 0:
                # Filter room types by name if provided, otherwise get all room types for that hotel
                room_types = hotel.room_types.filter(room_name__icontains=room_name) if room_name else hotel.room_types.all()

                # Serialize the hotel with the filtered room types
                available_hotels.append({
                    'hotel_name': hotel.name,
                    'location': hotel.location,
                    'price_per_night': str(hotel.price_per),
                    'available_rooms': available_rooms,
                    'room_types': RoomTypeSerializer(room_types, many=True).data,  # Serialize the room types
                    'check_in_date': check_in_date
                })

        if not available_hotels:
            return Response({"error": "No hotels found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)

        return Response(available_hotels, status=status.HTTP_200_OK)




