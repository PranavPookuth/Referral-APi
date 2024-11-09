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
            "total_points_for_referred_user": user.points
        }, status=status.HTTP_201_CREATED)




class UserPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "user_email": user.email,
            "points_balance": user.points
        })


