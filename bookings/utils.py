# bookings/utils.py
import os
from io import BytesIO
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage # Import EmailMessage
from weasyprint import HTML, CSS

def generate_ticket_pdf(booking):
    """Generates a PDF ticket for a given booking object."""
    
    # Render the HTML template with booking context
    html_string = render_to_string("bookings/ticket_template.html", {"booking": booking})
    
    # Basic CSS for the PDF
    css_string = """
        @page { size: A6; margin: 0.5cm; }
        body { font-family: 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', sans-serif; font-size: 10pt; }
        h1 { font-size: 16pt; text-align: center; margin-bottom: 1cm; color: #333; }
        .ticket-info { border: 1px solid #ccc; padding: 0.5cm; border-radius: 5px; background-color: #f9f9f9; }
        .ticket-info p { margin: 0.2cm 0; }
        .ticket-info strong { color: #555; }
        .footer { text-align: center; font-size: 8pt; color: #777; margin-top: 1cm; }
    """
    
    # Create WeasyPrint HTML object
    html = HTML(string=html_string, base_url=settings.BASE_DIR)
    
    # Create WeasyPrint CSS object
    css = CSS(string=css_string, font_config=None) # Use system fonts
    
    # Generate PDF in memory
    pdf_file = BytesIO()
    html.write_pdf(pdf_file, stylesheets=[css])
    pdf_file.seek(0)
    
    return pdf_file # Return the BytesIO object containing the PDF data

def send_ticket_email(booking):
    """Generates the ticket PDF and emails it to the user."""
    try:
        # Generate PDF
        pdf_buffer = generate_ticket_pdf(booking)
        pdf_filename = f"ticket_booking_{booking.pk}_event_{booking.event.pk}.pdf"

        # Prepare email content
        subject = render_to_string("bookings/email/ticket_confirmation_subject.txt", {"booking": booking}).strip()
        body = render_to_string("bookings/email/ticket_confirmation_body.txt", {"booking": booking})
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [booking.user.email]

        # Create EmailMessage object
        email = EmailMessage(
            subject,
            body,
            from_email,
            to_email,
        )

        # Attach the PDF
        email.attach(pdf_filename, pdf_buffer.getvalue(), "application/pdf")

        # Send the email
        email.send()
        print(f"Successfully sent ticket email for booking {booking.pk} to {booking.user.email}")
        return True
    except Exception as e:
        # Log the error appropriately in a real application
        print(f"Error sending ticket email for booking {booking.pk}: {e}")
        return False

