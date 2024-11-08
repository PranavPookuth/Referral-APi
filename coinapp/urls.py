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


]