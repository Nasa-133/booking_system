# bookings/models.py
from django.db import models
from django.conf import settings # To link to the User model (settings.AUTH_USER_MODEL)
from django.core.validators import MinValueValidator # To ensure quantity is at least 1
from django.utils.translation import gettext_lazy as _ # For internationalization of choices

# Import Event model using a direct import or string reference
# Using direct import here for clarity, ensure no circular dependencies
from events.models import Event 

class Booking(models.Model):
    """ Represents a ticket booking made by a user for a specific event.
        Tracks the user, event, quantity, price, status, and payment details.
    """
    
    # Define choices for the booking status field
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending Payment")
        CONFIRMED = "confirmed", _("Confirmed")
        CANCELLED = "cancelled", _("Cancelled")
        # Potentially add FAILED status if needed
        # FAILED = "failed", _("Payment Failed")

    # Foreign Key to the User model (using settings.AUTH_USER_MODEL is recommended)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, # If user is deleted, their bookings are also deleted
        related_name="bookings", # Allows accessing user.bookings
        help_text="The user who made the booking."
    )
    # Foreign Key to the Event model
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, # If event is deleted, associated bookings are deleted
        related_name="bookings", # Allows accessing event.bookings
        help_text="The event being booked."
    )
    # Number of tickets booked
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], # Ensure at least one ticket is booked
        help_text="Number of tickets booked."
    )
    # Total price for the booking (calculated based on event price and quantity)
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        editable=False, # Calculated automatically, should not be edited directly
        help_text="Total price for this booking (event.price * quantity)."
    )
    # Status of the booking (e.g., pending payment, confirmed, cancelled)
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.PENDING,
        help_text="The current status of the booking."
    )
    # Timestamp when the booking was created
    created_at = models.DateTimeField(
        auto_now_add=True, # Automatically set when the object is first created
        help_text="Timestamp when the booking was created."
    )
    # Timestamp when the booking was last updated
    updated_at = models.DateTimeField(
        auto_now=True, # Automatically set whenever the object is saved
        help_text="Timestamp when the booking was last updated."
    )
    # Field to store the Stripe Session ID or Payment Intent ID for reference
    stripe_payment_intent_id = models.CharField(
        max_length=255, 
        blank=True, # Can be blank initially
        null=True, # Can be null initially
        help_text="Stripe Payment Intent ID or Session ID associated with this booking."
    )

    def __str__(self):
        """ String representation of the Booking object. """
        return f"Booking {self.id} by {self.user.username} for {self.event.title} ({self.status})"

    def save(self, *args, **kwargs):
        """ Override the save method to automatically calculate the total price
            before saving the booking instance.
        """
        # Calculate total price based on event price and quantity if not already set
        # or if quantity/event changes (though event change is unlikely post-creation)
        if self.event and self.quantity:
            self.total_price = self.event.price * self.quantity
        super().save(*args, **kwargs) # Call the original save method

    class Meta:
        """ Meta options for the Booking model. """
        ordering = ["-created_at"] # Default ordering for bookings (most recent first)
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        # Optional: Ensure a user cannot double-book the exact same event in pending state
        # Consider constraints based on your specific business logic
        # unique_together = (
        #     ("user", "event", "status"), # Example: Prevent duplicate pending bookings
        # )

