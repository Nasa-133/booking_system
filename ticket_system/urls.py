# ticket_system/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView # Import TemplateView
from django.conf import settings # To serve static files during development
from django.conf.urls.static import static # To serve static files during development

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # User Authentication and Management
    path("users/", include("users.urls")), # Custom user views (signup, dashboard)
    path("users/", include("django.contrib.auth.urls")), # Built-in auth views (login, logout, password reset)
    
    # Core Application URLs
    path("events/", include("events.urls")), # Event listing and detail views
    path("bookings/", include("bookings.urls")), # Booking creation (and potentially list/detail later)
    path("payments/", include("payments.urls")), # Payment initiation, confirmation, webhook

    # Simple home page view using TemplateView
    path("", TemplateView.as_view(template_name="home.html"), name="home"), 
]

# Serve static files during development (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT if hasattr(settings, 'STATIC_ROOT') else settings.STATICFILES_DIRS[0])
    # Note: In production, web server (e.g., Nginx) should handle static files.

