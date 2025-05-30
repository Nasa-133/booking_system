# payments/urls.py
from django.urls import path
from .views import initiate_payment, payment_success, payment_cancelled, stripe_webhook # Import views

urlpatterns = [
    path("initiate/<int:booking_pk>/", initiate_payment, name="initiate_payment"),
    path("success/<int:booking_pk>/", payment_success, name="payment_success"), # Pass booking_pk for context
    path("cancelled/", payment_cancelled, name="payment_cancelled"),
    path("webhook/", stripe_webhook, name="stripe_webhook"),
]

