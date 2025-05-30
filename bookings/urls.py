# bookings/urls.py
from django.urls import path
from .views import create_booking # Import the booking creation view
# Import other booking views like list or detail if created later

urlpatterns = [
    # URL for handling the booking creation POST request from the event detail page
    path("create/<int:event_pk>/", create_booking, name="create_booking"),
    # Add URLs for booking list, detail, etc. here later if needed
    # path("", booking_list, name="booking_list"),
    # path("<int:booking_pk>/", booking_detail, name="booking_detail"),
]

