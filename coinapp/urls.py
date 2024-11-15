from .import views
from django.urls import path
from .views import *


urlpatterns = [

    # login register logout

    path('register/', views.RegisterView.as_view(), name='user-register'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/',Usercreateview.as_view(),name='user'),
    path('users/<int:pk>/',Userdetails.as_view(),name='user-details'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    #coin pusrchase
    path('purchase-coin/', CoinPurchaseView.as_view(), name='purchase-coin'),
    path('user-points/', UserPointsView.as_view(), name='user-points'),

    #hotel booking
    path('hotels/', views.HotelListCreateView.as_view(), name='hotel-list-create'),
    path('hotels/<int:pk>/', views.hotelview.as_view(), name='hotel-detail'),
    path('hotels/<int:pk>/', views.HotelDetailView.as_view(), name='hotel-detail'),
    path('hotel/<int:pk>/', HotelDetailView.as_view(), name='hotel-detail'),

    # URL for updating hotel booking (PUT method)
    path('hotel-booking/<int:pk>/', HotelBookingView.as_view(), name='hotel-booking'),
    path('book-hotel/', views.HotelBookingView.as_view(), name='hotel-booking'),
    path('hotels/search/', HotelSearchView.as_view(), name='hotel-search'),
    path('hotels/book/', HotelBookingView.as_view(), name='hotel-booking'),
    path('booking-details/<int:booking_id>/', HotelBookingDetailsView.as_view(), name='booking_details'),
    path('hotel/bookings/<int:pk>/', TotalBookingDetailView.as_view(), name='hotel-booking-count'),


]



