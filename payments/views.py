# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse # For webhook response
from django.views.decorators.csrf import csrf_exempt # For webhook
from django.utils import timezone

from bookings.models import Booking
# Import the processor factory and custom exception
from .processors import get_payment_processor, PaymentProcessingError

@login_required
def initiate_payment(request, booking_pk):
    """ Initiates the payment process using the configured payment processor.
        - Fetches the pending booking.
        - Gets the payment processor instance.
        - Calls the processor's initiate_payment method.
        - Renders the template with context returned by the processor.
    """
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user, status=Booking.Status.PENDING)

    # Prevent payment initiation if the event has already passed
    if booking.event.date < timezone.now():
        messages.error(request, "This event has already passed. Cannot initiate payment.")
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return redirect("event_detail", pk=booking.event.pk)

    try:
        # Get the configured payment processor instance (Bridge Pattern)
        payment_processor = get_payment_processor()
        
        # Call the processor's method to initiate payment (Bridge Pattern)
        # The processor handles the specific logic (e.g., creating Stripe session)
        # and returns the necessary context for the template.
        payment_context = payment_processor.initiate_payment(request, booking)

        # Add the booking to the context for the template
        context = {
            "booking": booking,
            **payment_context # Merge context from the processor (e.g., session_id, publishable_key)
        }
        return render(request, "payments/initiate_payment.html", context)

    except PaymentProcessingError as e:
        # Handle errors raised by the payment processor
        messages.error(request, f"Payment processing error: {e}")
        return redirect("event_detail", pk=booking.event.pk)
    except Exception as e:
        # Handle other unexpected errors
        messages.error(request, f"An unexpected error occurred: {e}")
        return redirect("event_detail", pk=booking.event.pk)

@login_required
def payment_success(request, booking_pk):
    """ Displays a success page after the user is redirected back from the payment provider.
        Relies on the webhook for actual confirmation.
    """
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user)
    
    if booking.status == Booking.Status.CONFIRMED:
        messages.success(request, "Payment successful! Your booking is confirmed.")
    elif booking.status == Booking.Status.PENDING:
        messages.info(request, "Payment processing. Your booking will be confirmed shortly via email.")
    else:
        messages.warning(request, f"Your booking status is currently {booking.get_status_display()}.")

    context = {"booking": booking}
    return render(request, "payments/payment_success.html", context)

@login_required
def payment_cancelled(request):
    """ Displays a cancellation page if the user cancels the payment process. """
    messages.warning(request, "Payment was cancelled. Your booking remains pending. You can try paying again later.")
    return render(request, "payments/payment_cancelled.html")

@csrf_exempt # Required for webhooks
def payment_webhook(request):
    """ Handles incoming webhook events by delegating to the configured payment processor.
        This view acts as the entry point and uses the Bridge pattern to call the
        appropriate processor's webhook handler.
    """
    try:
        # Get the configured payment processor instance (Bridge Pattern)
        payment_processor = get_payment_processor()
        
        # Delegate webhook handling to the processor (Bridge Pattern)
        # The processor handles signature verification and event processing.
        response = payment_processor.handle_webhook(request)
        return response
    except Exception as e:
        # Log unexpected errors in the webhook view itself
        print(f"Unexpected error in webhook view: {e}")
        return HttpResponse(status=500) # Internal Server Error

