import uuid

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
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price_per= models.DecimalField(max_digits=10, decimal_places=2)  # Price per night in currency
    discount_per_point = models.DecimalField(max_digits=5, decimal_places=2, default=0.1)  # Discount per point
    available_rooms = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.location}"


class HotelBooking(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotel_bookings")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="bookings")
    number_of_rooms = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    points_used = models.PositiveIntegerField(default=0)
    booking_date = models.DateTimeField(auto_now_add=True )
    def __str__(self):
        return f"Booking by {self.name.email} at {self.hotel.name} for {self.number_of_rooms} rooms on{self.booking_date}"

    def apply_discount(self):
        """
        Calculate the discount based on points used, apply it to the total price, and update the total price.
        """
        if self.points_used > 0:
            # Discount per point is 10 rupees
            discount_per_point = Decimal(10)
            discount = Decimal(self.points_used) * discount_per_point  # Discount based on points used

            # Ensure the discount does not exceed 50% of the total price
            max_discount = self.total_price * Decimal('0.5')  # Max discount is 50% of total price
            self.discount_applied = min(discount, max_discount)  # Apply the lesser of discount or max discount

            # Apply the discount to the total price, ensuring it doesn't go below zero
            self.total_price -= self.discount_applied
            self.total_price = max(self.total_price, Decimal('0.00'))  # Prevent negative total price
        else:
            # If no points are used, there is no discount
            self.discount_applied = Decimal('0.00')

        self.save()


