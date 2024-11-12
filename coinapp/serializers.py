from django.contrib.auth import  authenticate
from rest_framework import serializers
from .models import *
import uuid
import random
from django.core.mail import send_mail
from decimal import Decimal



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    mobile_number = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_number', 'password', 'confirm_password', 'referral_code']

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

            # Create new user
            username = str(uuid.uuid4())[:8]
            user = User.objects.create_user(
                email=validated_data['email'],
                username=username,
                name=validated_data['name'],
                mobile_number=validated_data['mobile_number'],
                password=validated_data['password'],
                referred_by=referred_by,
                is_active=False
            )

            if referred_by:
                referred_by.points += 10
                referred_by.save()

                # Create a Referral record
                Referral.objects.create(
                    referred_by=referred_by,
                    referred_user=user,
                    points_awarded=10  # Set points awarded
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

class CoinPurchaseSerializer(serializers.ModelSerializer):
    number_of_coins=serializers.IntegerField(required=True)
    class Meta:
        model = CoinPurchase
        fields = ['user', 'referred_by', 'number_of_coins', 'purchase_date', 'points_awarded_to_referrer']


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'


class HotelBookingSerializer(serializers.ModelSerializer):
    name = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    hotel = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
    room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    points_used = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = HotelBooking
        fields = ['name', 'hotel', 'room_type', 'number_of_rooms', 'points_used']

    def validate(self, data):
        # Fetch the user and hotel from the validated data
        name = data.get('name')
        hotel_id = data.get('hotel')
        room_type_id = data.get('room_type')
        points_used = data.get('points_used', 0)

        try:
            user = User.objects.get(id=name.id)  # Get user by ID from ForeignKey field
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        try:
            hotel = Hotel.objects.get(id=hotel_id.id)  # Get hotel by ID from ForeignKey field
        except Hotel.DoesNotExist:
            raise serializers.ValidationError("Hotel not found.")

        # Validate room type selection
        room_type = RoomType.objects.filter(hotel=hotel, id=room_type_id.id).first()
        if not room_type:
            raise serializers.ValidationError(f"Room type with id '{room_type_id}' not found for this hotel.")

        # Check if user has enough points
        if points_used > user.points:
            raise serializers.ValidationError("Not enough points.")

        # Check if hotel has enough available rooms
        if room_type.available_rooms < data['number_of_rooms']:
            raise serializers.ValidationError("Not enough available rooms for this room type.")

        # Calculate total price and discount
        total_price = room_type.price_per_night * data['number_of_rooms']
        discount_per_point = 10  # 10 rupees per point
        discount = points_used * discount_per_point
        max_discount = total_price * Decimal('0.5')  # Max discount is 50% of total price
        actual_discount = min(discount, max_discount)

        # Apply discount to total price
        discounted_price = total_price - actual_discount
        final_price = max(discounted_price, Decimal('0.00'))  # Ensure price is not negative

        # Store the total price, discount, and remaining points
        data['total_price'] = final_price
        data['discount_applied'] = actual_discount
        data['remaining_points'] = user.points - points_used  # This is just for calculation, not for saving

        # Add user, hotel, and room type to the data
        data['name'] = user
        data['hotel'] = hotel
        data['room_type'] = room_type

        return data


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['id', 'room_name', 'price_per_night', 'available_rooms']

class HotelSerializer(serializers.ModelSerializer):
    room_types = RoomTypeSerializer(many=True)  # Nested RoomType serializer

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'location', 'price_per', 'available_rooms', 'room_types']

    def create(self, validated_data):
        # Extract room types data from the request
        room_types_data = validated_data.pop('room_types')

        # Create the hotel instance
        hotel = Hotel.objects.create(**validated_data)

        # Create RoomType instances and associate them with the hotel
        for room_type_data in room_types_data:
            RoomType.objects.create(hotel=hotel, **room_type_data)

        return hotel

    def update(self, instance, validated_data):
        room_types_data = validated_data.pop('room_types', None)

        # Update the basic fields for the hotel
        instance = super().update(instance, validated_data)

        # Update room types
        if room_types_data is not None:
            # Clear the existing room types first if necessary
            instance.room_types.clear()

            # Add new room types to the hotel
            for room_data in room_types_data:
                room_type, created = RoomType.objects.update_or_create(
                    hotel=instance,
                    room_name=room_data['room_name'],
                    defaults={'price_per_night': room_data['price_per_night'], 'available_rooms': room_data['available_rooms']}
                )
                instance.room_types.add(room_type)

        return instance


class HotelBookingSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(write_only=True)
    room_type_name = serializers.CharField(write_only=True)
    check_in_date = serializers.DateField(write_only=True)

    # Include user-related fields
    user_name = serializers.CharField(source='user.username', read_only=True)  # Include username

    class Meta:
        model = HotelBooking
        fields = ['hotel_name', 'room_type_name', 'number_of_rooms', 'check_in_date', 'points_used', 'total_price',
                  'name', 'user', 'user_name']

    def create(self, validated_data):
        hotel_name = validated_data['hotel_name']
        room_type_name = validated_data['room_type_name']
        number_of_rooms = validated_data['number_of_rooms']
        points_used = validated_data['points_used']
        check_in_date = validated_data['check_in_date']
        user = validated_data.get('user', None)

        # Look up the Hotel by name
        try:
            hotel = Hotel.objects.get(name=hotel_name)
        except Hotel.DoesNotExist:
            raise serializers.ValidationError(f"Hotel with name '{hotel_name}' not found.")

        # Look up the RoomType by name and filter by hotel
        try:
            room_type = RoomType.objects.get(room_name=room_type_name, hotel=hotel)
        except RoomType.DoesNotExist:
            raise serializers.ValidationError(f"Room type '{room_type_name}' not found in hotel '{hotel_name}'.")

        # Calculate the total price based on the room type and number of rooms
        total_price = room_type.price_per_night * number_of_rooms

        # Create the booking
        booking = HotelBooking.objects.create(
            hotel=hotel,
            room_type=room_type,
            number_of_rooms=number_of_rooms,
            total_price=total_price,
            points_used=points_used,
            check_in_date=check_in_date,
            user=user,
            name=user  # Ensure the 'name' field is set to the same User instance
        )

        return booking
