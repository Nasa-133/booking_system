# payments/processors.py
import abc
import stripe
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse # For webhook response
from bookings.models import Booking
from bookings.utils import send_ticket_email

class PaymentProcessor(abc.ABC):
    """ Abstract Base Class defining the interface for payment processors.
        This acts as the Abstraction in the Bridge pattern.
    """
    
    @abc.abstractmethod
    def initiate_payment(self, request, booking):
        """ Initiates the payment process for a given booking.
            Should return context data needed for the frontend (e.g., session ID, keys) 
            or raise an exception on failure.
        """
        pass

    @abc.abstractmethod
    def handle_webhook(self, request):
        """ Handles incoming webhook events from the payment provider.
            Should verify the webhook signature and update booking status accordingly.
            Returns an HttpResponse (e.g., status 200 for success, 400/500 for errors).
        """
        pass

class StripePaymentProcessor(PaymentProcessor):
    """ Concrete implementation of PaymentProcessor for Stripe.
        This acts as the Concrete Implementor in the Bridge pattern.
    """
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    def initiate_payment(self, request, booking):
        """ Creates a Stripe Checkout Session. """
        try:
            success_url = request.build_absolute_uri(reverse("payment_success", kwargs={"booking_pk": booking.pk}))
            cancel_url = request.build_absolute_uri(reverse("payment_cancelled"))

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Tickets for {booking.event.title}",
                                "description": f"{booking.quantity} x ticket(s)",
                            },
                            "unit_amount": int(booking.event.price * 100),
                        },
                        "quantity": booking.quantity,
                    },
                ],
                mode="payment",
                metadata={"booking_pk": booking.pk},
                customer_email=request.user.email,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            # Store session ID for reference
            booking.stripe_payment_intent_id = checkout_session.id
            booking.save()

            # Return context needed for the template
            return {
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                "stripe_session_id": checkout_session.id
            }
        except stripe.error.StripeError as e:
            print(f"Stripe error during payment initiation for booking {booking.pk}: {e}")
            raise PaymentProcessingError(f"Stripe error: {e}") from e
        except Exception as e:
            print(f"Unexpected error during payment initiation for booking {booking.pk}: {e}")
            raise PaymentProcessingError(f"Unexpected error: {e}") from e

    def handle_webhook(self, request):
        """ Handles Stripe webhook events, specifically checkout.session.completed. """
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
        except ValueError as e:
            print(f"Stripe Webhook error: Invalid payload - {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            print(f"Stripe Webhook error: Invalid signature - {e}")
            return HttpResponse(status=400)

        # Handle the checkout.session.completed event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            booking_pk = session.get("metadata", {}).get("booking_pk")
            payment_status = session.get("payment_status")

            if booking_pk and payment_status == "paid":
                try:
                    booking = Booking.objects.get(pk=booking_pk)
                    if booking.status == Booking.Status.PENDING:
                        booking.status = Booking.Status.CONFIRMED
                        booking.stripe_payment_intent_id = session.get("payment_intent")
                        booking.save()
                        print(f"Webhook: Booking {booking_pk} confirmed via Stripe.")
                        send_ticket_email(booking)
                    else:
                        print(f"Webhook: Booking {booking_pk} already processed (status: {booking.status}). Ignoring.")
                except Booking.DoesNotExist:
                    print(f"Webhook Error: Booking {booking_pk} not found.")
                    return HttpResponse(status=404)
                except Exception as e:
                    print(f"Webhook Error: Error processing booking {booking_pk}: {e}")
                    return HttpResponse(status=500)
            else:
                print(f"Webhook: Received session {session.id} for booking {booking_pk} but payment status is \'{payment_status}\' or booking_pk missing.")
        else:
            print(f"Webhook: Unhandled event type {event["type"]}")

        return HttpResponse(status=200)

# Custom exception for payment errors
class PaymentProcessingError(Exception):
    pass

# --- Factory Function (Optional but useful) ---
# This function selects the appropriate processor based on settings
def get_payment_processor():
    """ Returns an instance of the configured payment processor. """
    # For now, we only have Stripe
    # In the future, this could read from settings.PAYMENT_PROCESSOR_CLASS
    return StripePaymentProcessor()

