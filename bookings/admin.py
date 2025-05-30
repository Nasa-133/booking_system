# bookings/admin.py
from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for the Booking model."""
    list_display = ("id", "user", "event", "quantity", "total_price", "status", "created_at")
    list_filter = ("status", "event__category", "event__date", "created_at") # Filter by status and event details
    search_fields = ("id", "user__username", "user__email", "event__title", "stripe_payment_intent_id")
    ordering = ("-created_at",)
    list_select_related = ("user", "event") # Optimize queries by fetching related objects
    readonly_fields = ("total_price", "created_at", "updated_at", "stripe_payment_intent_id") # Fields calculated or set externally
    date_hierarchy = "created_at"

    # Customize the detail view fields
    fieldsets = (
        ("Booking Information", {
            "fields": ("id", "user", "event", "quantity", "total_price", "status")
        }),
        ("Payment Information", {
            "fields": ("stripe_payment_intent_id",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",) # Make this section collapsible
        }),
    )
    # Override the default readonly fields in fieldsets to ensure they appear
    readonly_fields = ("id", "user", "event", "total_price", "created_at", "updated_at", "stripe_payment_intent_id")

    def get_readonly_fields(self, request, obj=None):
        # Make all fields readonly in the admin change view after creation
        # if obj: # obj is not None, so this is an existing booking
        #     return self.readonly_fields + ('quantity', 'status') # Add fields you want readonly on edit
        return self.readonly_fields

    # Optional: Add actions like marking bookings as cancelled (use with caution)
    # actions = ["mark_as_cancelled"]
    # def mark_as_cancelled(self, request, queryset):
    #     queryset.update(status="cancelled")
    #     # Add logic here to potentially refund or adjust ticket counts if needed
    # mark_as_cancelled.short_description = "Mark selected bookings as Cancelled"

