from django.contrib import admin
from .models import *
# Register your models here.
# Customizing the Hotel Admin view
class UserAdmin(admin.ModelAdmin):
    list_display = (    'email', 'name', 'mobile_number', 'is_verified', 'points',
        'referral_code', 'referred_by', 'is_staff', 'is_active'
    )
    list_filter = ('is_verified', 'is_staff', 'is_active', 'groups')
    search_fields = ('email', 'name', 'mobile_number', 'referral_code')
class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1  # Allows adding additional room types directly in the hotel admin form

class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price_per', 'available_rooms', 'check_in_date')
    search_fields = ('name', 'location')
    list_filter = ('location', 'check_in_date')
    inlines = [RoomTypeInline]  # Allows editing RoomType directly in the Hotel form

class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'price_per_night', 'available_rooms', 'hotel')
    search_fields = ('room_name', 'hotel__name')  # Allows searching by hotel name
    list_filter = ('hotel',)

class RoomAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'date', 'available_rooms')
    list_filter = ('hotel', 'date')

class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'room_type', 'number_of_rooms', 'total_price', 'booking_date', 'check_in_date')
    search_fields = ('user__email', 'hotel__name')
    list_filter = ('hotel', 'check_in_date')
    readonly_fields = ('booking_date',)

# Registering models with the custom admin classes
admin.site.register(User, UserAdmin)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(RoomAvailability, RoomAvailabilityAdmin)
admin.site.register(HotelBooking, HotelBookingAdmin)
