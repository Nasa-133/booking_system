# bookings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction # For atomic database operations
from django.urls import reverse
from django.utils import timezone # To check event dates
from django.conf import settings # To access settings like STRIPE keys

from .models import Booking
from events.models import Event # Import Event model

@login_required # Ensure user is logged in to book
@transaction.atomic # Wrap the view in a database transaction
def create_booking(request, event_pk):
    """ Handles the creation of a new booking for a specific event.
        - Validates the requested quantity.
        - Checks if sufficient tickets are available.
        - Creates a Booking instance with status "pending".
        - Decreases the event's available_tickets count.
        - Redirects to the payment initiation page upon successful booking creation.
        Uses transaction.atomic to ensure ticket availability check and booking creation
        are performed as a single, indivisible operation to prevent race conditions.
    """
    # Retrieve the event, ensuring it exists and is upcoming
    event = get_object_or_404(Event, pk=event_pk, date__gte=timezone.now())

    if request.method == "POST":
        # Process the booking form submission
        try:
            # Get and validate the requested quantity
            quantity = int(request.POST.get("quantity", 1))
            if quantity <= 0:
                raise ValueError("Quantity must be a positive integer.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity specified. Please enter a valid number.")
            return redirect("event_detail", pk=event.pk)

        # --- Atomic Transaction Starts Here --- 
        # Lock the event row for update to prevent race conditions during check/update.
        # NOTE: select_for_update() provides stronger locking guarantees on databases
        # like PostgreSQL. SQLite's support is limited, but transaction.atomic still helps.
        try:
            # Re-fetch the event within the transaction with locking
            event_locked = Event.objects.select_for_update().get(pk=event_pk)
        except Event.DoesNotExist:
             # Should not happen if initial get_object_or_404 worked, but good practice
             messages.error(request, "Event not found or has already passed.")
             return redirect("event_list")

        # Check if enough tickets are available (using the locked event instance)
        if event_locked.available_tickets >= quantity:
            # Create the booking instance
            booking = Booking.objects.create(
                user=request.user,
                event=event_locked,
                quantity=quantity,
                status=Booking.Status.PENDING, # Initial status is pending
                # total_price is calculated automatically in the Booking model's save() method
            )
            
            # Decrease the available tickets count for the event
            event_locked.available_tickets -= quantity
            event_locked.save()

            # --- Atomic Transaction Ends Here (Commit) --- 

            messages.success(request, f"Booking created for {quantity} ticket(s). Please proceed to payment.")
            # Redirect to the payment initiation view, passing the new booking's PK
            return redirect(reverse("initiate_payment", kwargs={"booking_pk": booking.pk}))
        
        else:
            # --- Atomic Transaction Ends Here (Rollback if error occurred before commit) ---
            messages.error(request, f"Sorry, only {event_locked.available_tickets} ticket(s) are available for this event.")
            return redirect("event_detail", pk=event.pk)

    else:
        # If the view is accessed via GET, it's not a valid booking attempt
        messages.error(request, "Invalid request method.")
        return redirect("event_detail", pk=event.pk)

# Note: The initiate_payment view is now in payments/views.py
# We keep the import here as it was previously defined but now moved.
# from payments.views import initiate_payment 

# Potential future views:
# - booking_list(request): Display a list of the current user's bookings.
# - booking_detail(request, booking_pk): Display details of a specific booking.

