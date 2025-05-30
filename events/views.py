# events/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q # For complex queries (e.g., OR conditions)
from django.utils import timezone # To filter events based on current time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # Optional: For pagination

from .models import Event

def event_list(request):
    """ Displays a list of upcoming events.
        Handles filtering by search query (title, location) and category.
        Also retrieves distinct categories for the filter dropdown.
        Optional pagination can be added.
    """
    # Start with a base queryset of upcoming events
    base_queryset = Event.objects.filter(date__gte=timezone.now()).select_related() # select_related can optimize if needed later
    queryset = base_queryset
    
    # Get search and filter parameters from the GET request
    query = request.GET.get("q")
    category = request.GET.get("category")

    # Apply search filters if parameters are provided
    if query:
        # Filter by title OR location containing the query (case-insensitive)
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        )
    
    if category:
        # Filter by exact category match (case-insensitive)
        queryset = queryset.filter(category__iexact=category)

    # Get distinct categories from *upcoming* events for the filter dropdown
    # Using the base_queryset ensures categories shown are relevant to available events
    categories = base_queryset.values_list("category", flat=True).distinct().order_by("category")

    # --- Optional: Add Pagination --- 
    # page = request.GET.get("page", 1)
    # paginator = Paginator(queryset, 10) # Show 10 events per page
    # try:
    #     events_page = paginator.page(page)
    # except PageNotAnInteger:
    #     events_page = paginator.page(1)
    # except EmptyPage:
    #     events_page = paginator.page(paginator.num_pages)
    # ----------------------------- 

    context = {
        "events": queryset, # Pass the filtered queryset to the template (or events_page if using pagination)
        # "events": events_page, # Use this if pagination is enabled
        "categories": categories, # Pass distinct categories for the dropdown
        "selected_category": category, # Pass selected category back to template to keep dropdown state
        "search_query": query, # Pass search query back to template to keep input state
    }
    return render(request, "events/event_list.html", context)

def event_detail(request, pk):
    """ Displays the details for a specific upcoming event.
        Uses get_object_or_404 to handle cases where the event doesn't exist or has passed.
    """
    # Retrieve the specific event by its primary key (pk)
    # Ensure the event exists and its date is in the future (or present)
    event = get_object_or_404(Event, pk=pk, date__gte=timezone.now())
    
    # The booking form is part of the template, logic is handled by create_booking view
    context = {
        "event": event,
    }
    return render(request, "events/event_detail.html", context)

