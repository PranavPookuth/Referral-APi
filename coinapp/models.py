import uuid
from datetime import timezone

from django.db import models

# Create your models here.
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, Permission, Group, PermissionsMixin
from django.db import models
from decimal import Decimal


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, referred_by=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, referred_by=referred_by, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True,default="123456789")
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_secret_key = models.CharField(max_length=32, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    DOB = models.DateField(null=True, blank=True)
    points = models.IntegerField(default=0)
    referral_code = models.CharField(max_length=8, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self',related_name='referrals_by',on_delete=models.CASCADE,null=True,blank=True)
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4().hex)[:8]
        super().save(*args, **kwargs)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_number', 'name']
    objects = CustomUserManager()

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True
    )

    def __str__(self):
        return self.email


class Referral(models.Model):
    referred_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_users')
    referral_code = models.CharField(max_length=8, unique=True, default=uuid.uuid4, editable=False)
    def __str__(self):
        return f"{self.referred_user.email} referred by {self.referred_by.email}"

    def referred_user_name(self):
        return self.referred_user.name


class CoinPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coin_purchases")
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="referrals_earning_points")
    number_of_coins = models.PositiveIntegerField(null=False,blank=False)
    purchase_date = models.DateTimeField(auto_now_add=True)
    points_awarded_to_referrer = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} purchased {self.number_of_coins} coins"

class Hotel(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    location = models.CharField(max_length=255)
    price_per = models.DecimalField(max_digits=10, decimal_places=2)  # Price per night in currency
    discount_per_point = models.DecimalField(max_digits=5, decimal_places=2, default=0.1)  # Discount per point
    available_rooms = models.PositiveIntegerField(default=0)
    check_in_date = models.DateField()
    room_types = models.ManyToManyField('RoomType', related_name="hotels", blank=True)

    def __str__(self):
        return f"Booking for {self.name} on {self.check_in_date}"

    def available_on_date(self, date, room_type_name=None):
        print(f"Checking availability for hotel: {self.name}, on {date}, for room type: {room_type_name}")

        # Check for specific availability for the given date (using RoomAvailability)
        availability = self.roomavailabilities.filter(date=date)

        if availability.exists():
            available_rooms = availability.first().available_rooms
            print(f"Found specific availability for {date}: {available_rooms} rooms")
        else:
            available_rooms = self.available_rooms  # Fallback to hotel-wide available rooms
            print(
                f"No specific availability found for {date}, fallback to hotel-wide availability: {available_rooms} rooms")

        # If room_type_name is provided, check for availability of the specific room type
        if room_type_name:
            room_type = self.room_types.filter(room_name__icontains=room_type_name).first()
            if room_type:
                print(f"Found room type {room_type_name} with {room_type.available_rooms} rooms available.")
                # Here we get the available rooms for the room type and return the minimum of room availability
                available_rooms_for_room_type = min(available_rooms, room_type.available_rooms)
                print(
                    f"Room type {room_type_name} has {room_type.available_rooms} rooms available. Limited by {available_rooms_for_room_type} available rooms.")
                return available_rooms_for_room_type
            print(f"Room type {room_type_name} not found.")
            return 0  # If no room type is found, return 0 available rooms

        return available_rooms


class RoomType(models.Model):
    room_name = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)  # Price for the room type
    available_rooms = models.PositiveIntegerField(default=0)  # Number of available rooms for this type
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="room_types_list", null=True)

    def __str__(self):
        return f"{self.room_name} - {self.hotel.name}"

class RoomAvailability(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="roomavailabilities")
    date = models.DateField()  # Date for room availability
    available_rooms = models.PositiveIntegerField(default=0)  # Number of rooms available on this date

    def __str__(self):
        return f"{self.hotel.name} - {self.date} - {self.available_rooms} rooms"

class HotelBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotel_bookings")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="bookings")
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="bookings", null=True)
    number_of_rooms = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    points_used = models.PositiveIntegerField(default=0)
    booking_date = models.DateTimeField(auto_now_add=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()

    def __str__(self):
        return f"Booking by {self.name.email} at {self.hotel.name} for {self.number_of_rooms} {self.room_type.room_name} rooms on {self.booking_date}"

    def get_total_nights(self):
        """
        Calculate the total number of nights for the booking based on check-in and check-out dates.
        """
        return (self.check_out_date - self.check_in_date).days

    def apply_discount(self):
        """
        Apply discount logic. This will now take into account the total number of nights.
        """
        total_nights = self.get_total_nights()
        total_price = self.room_type.price_per_night * total_nights * self.number_of_rooms

        # Discount logic
        if self.points_used > 0:
            discount_per_point = Decimal(10)  # e.g., 10 currency units per point
            discount = Decimal(self.points_used) * discount_per_point

            max_discount = total_price * Decimal('0.5')  # Max discount 50% of total price
            self.discount_applied = min(discount, max_discount)

            self.total_price = total_price - self.discount_applied
            self.total_price = max(self.total_price, Decimal('0.00'))  # Ensure the price is not negative
        else:
            self.discount_applied = Decimal('0.00')
            self.total_price = total_price

        self.save()