# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required # For function-based views
from django.contrib.auth.mixins import LoginRequiredMixin # For class-based views (if used later)
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages # To display feedback to the user

from .forms import SignUpForm

# User registration view using Django's generic CreateView
class SignUpView(generic.CreateView):
    """ Handles user registration using a class-based view.
        Displays the signup form and processes form submission.
    """
    form_class = SignUpForm
    # Redirect to the login page upon successful registration
    # reverse_lazy is used because URLs are not loaded when the file is imported
    success_url = reverse_lazy("login") 
    template_name = "users/signup.html" # Template used to render the signup form

    def form_valid(self, form):
        """ Processes the valid form upon submission.
            Saves the new user and redirects to the success URL.
            Optionally, could log the user in directly after signup.
        """
        user = form.save()
        messages.success(self.request, "Account created successfully! Please log in.")
        # Optional: Log the user in directly after signing up
        # login(self.request, user)
        # return redirect("dashboard") # Redirect to dashboard if logged in
        
        # Default behavior: redirect to success_url (login page)
        return super().form_valid(form)

    def form_invalid(self, form):
        """ Handles invalid form submissions.
            Re-renders the form with error messages.
        """
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

# Protected dashboard view using a function-based view and decorator
@login_required # Ensures only logged-in users can access this view
def dashboard(request):
    """ A simple dashboard view accessible only to logged-in users.
        Displays a welcome message.
    """
    # Context can be expanded later to show user-specific information (e.g., recent bookings)
    context = {
        "user": request.user
    }
    return render(request, "users/dashboard.html", context)

# Potential future views:
# - User Profile View (display/edit profile information)
# - User Bookings List View (display user's past and upcoming bookings)

