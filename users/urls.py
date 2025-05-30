# users/urls.py
from django.urls import path
from .views import SignUpView, dashboard # Import dashboard view

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("dashboard/", dashboard, name="dashboard"), # Add dashboard URL
    # Add other user-related URLs here later
]

