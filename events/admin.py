# events/admin.py
from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin configuration for the Event model."""
    list_display = ("title", "category", "date", "location", "price", "available_tickets", "total_tickets")
    list_filter = ("category", "date", "location")
    search_fields = ("title", "category", "location", "description") # Assuming description might be added later
    ordering = ("date",)
    # Make available_tickets editable, but be cautious
    # list_editable = ("available_tickets",) 
    # Add date hierarchy for easier navigation
    date_hierarchy = "date"

    # Customize the form if needed
    # fields = (...) # or fieldsets = (...)

