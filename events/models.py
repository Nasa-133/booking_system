# events/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Event(models.Model):
    """ Represents a bookable event within the system.
        Stores details like title, date, location, price, and ticket availability.
    """
    title = models.CharField(
        max_length=200,
        help_text="The main title of the event."
    )
    # Consider using a ForeignKey to a separate Category model for better organization and filtering
    category = models.CharField(
        max_length=100, 
        help_text="e.g., Concert, Workshop, Conference, Sports"
    )
    date = models.DateTimeField(
        help_text="The date and time when the event starts."
    )
    location = models.CharField(
        max_length=255,
        help_text="The physical address or venue of the event."
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="The price per ticket."
    )
    total_tickets = models.PositiveIntegerField(
        help_text="The total number of tickets initially available for this event."
    )
    # This field tracks the currently available tickets, decreased upon booking
    available_tickets = models.PositiveIntegerField(
        help_text="The number of tickets currently available for booking.",
        # editable=False # Consider making this non-editable directly in admin after initial setup
    )
    # Optional: Add a description field
    # description = models.TextField(blank=True, null=True, help_text="A detailed description of the event.")
    # Optional: Add an image field
    # image = models.ImageField(upload_to="event_images/", blank=True, null=True)

    def __str__(self):
        """ String representation of the Event object. """
        # Corrected f-string with single quotes for strftime format
        return f"{self.title} on {self.date.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """ Custom validation logic for the Event model.
            Ensures data integrity before saving.
        """
        super().clean() # Call parent clean method first
        
        # Ensure available tickets do not exceed total tickets
        if self.available_tickets is not None and self.total_tickets is not None:
             if self.available_tickets > self.total_tickets:
                 raise ValidationError({"available_tickets": "Available tickets cannot exceed total tickets."})
        
        # Ensure event date is not in the past (optional, depends on requirements)
        # Uncomment if events cannot be created or edited to be in the past
        # if self.date and self.date < timezone.now():
        #     raise ValidationError({"date": "Event date cannot be in the past."})

    def save(self, *args, **kwargs):
        """ Override the save method to ensure validation is called and 
            to set initial available_tickets if not provided.
        """
        # Set available_tickets equal to total_tickets on initial creation if not specified
        if self.pk is None and self.available_tickets is None and self.total_tickets is not None:
             self.available_tickets = self.total_tickets
             
        self.full_clean() # Call full_clean to run all model validators (including clean method)
        super().save(*args, **kwargs) # Call the original save method

    class Meta:
        """ Meta options for the Event model. """
        ordering = ["date"] # Order events by date by default in querysets
        verbose_name = "Event"
        verbose_name_plural = "Events"

