# Online Ticket Booking System

This is a Django-based web application for browsing events and booking tickets online.

## Features Implemented

*   **Project Scaffolding:** Django project `ticket_system` with core apps: `users`, `events`, `bookings`, `payments`.
*   **User Authentication:**
    *   User registration using username and email.
    *   User login and logout functionality leveraging Django's built-in authentication system.
    *   A protected dashboard view (`/users/dashboard/`) accessible only to logged-in users.
*   **Event Management:**
    *   `Event` model defined with title, category, date, location, price, total tickets, and available tickets.
    *   Event listing page (`/events/`) displaying upcoming events.
    *   Search functionality by keyword (title/location) and filtering by category.
    *   Event detail page (`/events/<pk>/`) showing full event information.
*   **Booking System:**
    *   `Booking` model linking users, events, quantity, price, and status.
    *   Users can select the number of tickets on the event detail page.
    *   Booking creation logic that atomically checks availability and updates `available_tickets` on the `Event` model.
*   **Payment Integration (Stripe - Test Mode with Bridge Pattern):**
    *   **Bridge Pattern Implemented:** Payment processing is refactored using the Bridge pattern for better decoupling and extensibility (see details below).
    *   Integration with Stripe Checkout via a `StripePaymentProcessor`.
    *   Redirects users to Stripe for secure payment processing.
    *   Uses Stripe webhooks (`/payments/webhook/`) handled by the processor to reliably confirm successful payments and update booking status to "confirmed".
    *   Success (`/payments/success/<booking_pk>/`) and cancellation (`/payments/cancelled/`) pages for user feedback.
*   **Ticket Generation & Delivery:**
    *   Generates a PDF ticket using WeasyPrint upon successful payment confirmation (triggered via webhook handler in the payment processor).
    *   Sends the generated PDF ticket as an email attachment to the user's registered email address using Django's email backend (configured for console output by default).
*   **Admin Panel:**
    *   Django's default admin interface (`/admin/`) is enabled.
    *   Custom admin configurations for `Event` and `Booking` models for easier management (filtering, search, display fields).
*   **Templating & Styling:**
    *   Uses Django templates for frontend rendering.
    *   Includes `base.html` for consistent layout and navigation.
    *   Templates for home, login, signup, dashboard, event list, event detail, payment initiation, success, and cancellation.
    *   Basic responsive CSS (`static/css/style.css`) for improved layout and mobile-friendliness.
*   **Configuration:**
    *   Settings configured to use environment variables (`.env` file) for sensitive data (Secret Key, Debug, Allowed Hosts, Stripe Keys, Email settings).
    *   Uses SQLite as the database backend.
*   **Code Quality:**
    *   Modular structure with separate apps for different functionalities.
    *   Detailed comments added throughout the codebase for clarity and maintainability.
*   **Dependencies:** `requirements.txt` generated for easy installation.

## Setup Instructions

1.  **Unzip the Project:** Extract the contents of the provided zip file.
2.  **Navigate to Project Directory:** Open your terminal and change into the project directory (`online_ticket_booking`).
3.  **Create Virtual Environment:**
    ```bash
    python3 -m venv venv
    ```
4.  **Activate Virtual Environment:**
    *   On macOS/Linux: `source venv/bin/activate`
    *   On Windows: `venv\Scripts\activate`
5.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
6.  **Configure Environment Variables:**
    *   Copy the example environment file: `cp .env.example .env` (or `copy .env.example .env` on Windows).
    *   Edit the `.env` file. **Crucially, replace placeholders**, especially `DJANGO_SECRET_KEY` (generate a new strong key) and your **Stripe Test Keys** (`STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`). You can get test keys from your Stripe dashboard.
7.  **Apply Database Migrations:**
    ```bash
    python manage.py migrate
    ```
8.  **Create Superuser (Optional):** To access the Django admin panel (`/admin/`):
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts.
9.  **Run Development Server:**
    ```bash
    python manage.py runserver
    ```
10. **Access the Application:** Open your web browser and go to `http://127.0.0.1:8000/`.
    *   Browse events at `/events/`.
    *   Sign up at `/users/signup/`.
    *   Login at `/users/login/`.
    *   Access the admin panel at `/admin/`.
11. **Test Payment Flow:**
    *   Register/Login.
    *   Find an event and click "View Details & Book".
    *   Enter quantity and click "Book Now".
    *   Click "Pay with Stripe".
    *   Use Stripe's test card details (e.g., card number 4242 4242 4242 4242, any future date, any 3-digit CVC, any ZIP code).
    *   Complete the test payment.
    *   You should be redirected to the success page.
    *   Check the console where `runserver` is running - you should see output indicating the webhook was received, the booking was confirmed, and the email (with PDF) was "sent" (printed to console by default).

## Bridge Design Pattern Implementation (Payment Processing)

You asked for an implementation of the Bridge pattern. It has now been applied to the **payment processing module** to decouple the payment logic from specific providers like Stripe.

**What is the Bridge Pattern?**

The Bridge pattern is a structural design pattern that decouples an abstraction from its implementation so that the two can vary independently. It's useful when you need to vary both the abstraction and its implementation, or when an implementation must be selected or switched at runtime.

**How it's Implemented Here:**

1.  **Abstraction (`payments/processors.py`):**
    *   An abstract base class `PaymentProcessor` is defined using Python's `abc` module.
    *   It declares abstract methods `initiate_payment(request, booking)` and `handle_webhook(request)`, defining the standard interface for any payment processor.
    *   This `PaymentProcessor` acts as the **Abstraction** part of the Bridge pattern.

2.  **Concrete Implementor (`payments/processors.py`):**
    *   The `StripePaymentProcessor` class inherits from `PaymentProcessor`.
    *   It provides the concrete implementation for the `initiate_payment` and `handle_webhook` methods using the Stripe API.
    *   This `StripePaymentProcessor` acts as the **Concrete Implementor** part of the Bridge pattern.

3.  **Client (`payments/views.py`):**
    *   The views (`initiate_payment`, `payment_webhook`) no longer contain direct Stripe API calls.
    *   Instead, they use a factory function `get_payment_processor()` (defined in `payments/processors.py`) to get an instance of the currently configured `PaymentProcessor` (which is `StripePaymentProcessor` in this case).
    *   The views then call the methods defined in the `PaymentProcessor` abstraction (e.g., `payment_processor.initiate_payment(...)`, `payment_processor.handle_webhook(...)`).
    *   The views act as the **Client** in the pattern, interacting only with the Abstraction.

**Why Use It Here?**

*   **Decoupling:** The payment views (`payments/views.py`) are now decoupled from the specifics of Stripe. They only know about the `PaymentProcessor` interface.
*   **Extensibility:** Adding a new payment provider (e.g., PayPal) becomes much easier:
    1.  Create a new class `PayPalPaymentProcessor(PaymentProcessor)` in `payments/processors.py` implementing the required methods.
    2.  Update the `get_payment_processor()` factory function (perhaps based on a Django setting) to return an instance of `PayPalPaymentProcessor` when needed.
    3.  **No changes would be required in the core view logic (`payments/views.py`)**. The views would seamlessly work with the new PayPal processor through the `PaymentProcessor` abstraction.

This implementation demonstrates how the Bridge pattern separates the high-level payment logic (in the views) from the low-level platform-specific details (in the processor classes), making the system more flexible and maintainable.

