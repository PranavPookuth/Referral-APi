from django.contrib.auth import  authenticate
from rest_framework import serializers
from .models import *
import uuid
import random
from django.core.mail import send_mail


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    mobile_number = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=True)  # Add username field

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'mobile_number', 'password', 'confirm_password', 'referral_code']

    def validate(self, data):
        # Password validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords must match.")

        email = data.get('email')
        mobile_number = data.get('mobile_number')

        try:
            user = User.objects.get(email=email, mobile_number=mobile_number)
            if user.is_verified:
                raise serializers.ValidationError({
                    'email': 'User with this email is already verified.',
                    'mobile_number': 'User with this mobile number is already verified.',
                })
            else:
                # If user exists but is not verified, allow OTP regeneration
                self.context['existing_user'] = user
        except User.DoesNotExist:
            pass

        # Validate referral code if provided
        referral_code = data.get('referral_code')
        if referral_code:
            try:
                referred_user = User.objects.get(referral_code=referral_code)
                data['referred_by'] = referred_user  # Save the referred user (the user who referred the new user)
            except User.DoesNotExist:
                raise serializers.ValidationError({'referral_code': 'Invalid referral code.'})
        return data

    def create(self, validated_data):
        # Handle OTP generation and sending for existing user
        if 'existing_user' in self.context:
            user = self.context['existing_user']
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )
            return user
        else:
            # Handle new user creation
            validated_data.pop('confirm_password')

            # Extract referred_by if it exists
            referred_by = validated_data.get('referred_by', None)

            # Create new user with custom username
            user = User.objects.create_user(
                email=validated_data['email'],
                username=validated_data['username'],  # Use the provided username
                name=validated_data['name'],
                mobile_number=validated_data['mobile_number'],
                password=validated_data['password'],
                referred_by=referred_by,  # Set referred_by field
                is_active=False  # The user should not be active until verified
            )

            # Create a referral record if the user was referred
            if referred_by:
                Referral.objects.create(
                    referred_by=referred_by,
                    referred_user=user,
                    referral_code=user.referral_code
                )

            # Generate OTP for new user
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            # Send OTP via email
            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )

            return user





class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_verified:
            raise serializers.ValidationError("Email not verified.")
        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

