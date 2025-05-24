import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import List, Optional
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()

class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        """Initialize the email service with configuration."""
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.enabled = settings.EMAIL_NOTIFICATIONS_ENABLED
    
    def send_email(self, to_email: str, subject: str, body_html: str, body_text: Optional[str] = None) -> bool:
        """
        Send an email to the specified recipient.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML content of the email
            body_text: Plain text content of the email (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.enabled:
            # Email notifications are disabled
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach plain text version
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            
            # Attach HTML version
            msg.attach(MIMEText(body_html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            # Log the error but don't raise, as notification failure
            # shouldn't disrupt the main application flow
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_swap_request_created_notification(self, to_email: str, requester_name: str, ride_date: datetime) -> bool:
        """
        Send notification when a swap request is created.
        
        Args:
            to_email: Email of the requested driver
            requester_name: Name of the requesting driver
            ride_date: Date of the ride
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "New Carpool Swap Request"
        
        # Format the date
        formatted_date = ride_date.strftime("%A, %B %d, %Y")
        
        html_body = f"""
        <html>
        <body>
            <h2>New Carpool Swap Request</h2>
            <p>Hello,</p>
            <p>{requester_name} has requested to swap their carpool duty with you for {formatted_date}.</p>
            <p>Please login to the Carpool Management App to review and respond to this request.</p>
            <p>Thank you for your participation in our carpool program.</p>
            <p>Best regards,<br>Carpool Management System</p>
        </body>
        </html>
        """
        
        text_body = f"""
        New Carpool Swap Request
        
        Hello,
        
        {requester_name} has requested to swap their carpool duty with you for {formatted_date}.
        
        Please login to the Carpool Management App to review and respond to this request.
        
        Thank you for your participation in our carpool program.
        
        Best regards,
        Carpool Management System
        """
        
        return self.send_email(to_email, subject, html_body, text_body)
    
    def send_swap_request_response_notification(self, to_email: str, responder_name: str, 
                                               ride_date: datetime, accepted: bool) -> bool:
        """
        Send notification when a swap request is accepted or rejected.
        
        Args:
            to_email: Email of the requesting driver
            responder_name: Name of the requested driver who responded
            ride_date: Date of the ride
            accepted: Whether the request was accepted
            
        Returns:
            bool: True if email sent successfully
        """
        status = "accepted" if accepted else "rejected"
        subject = f"Carpool Swap Request {status.capitalize()}"
        
        # Format the date
        formatted_date = ride_date.strftime("%A, %B %d, %Y")
        
        html_body = f"""
        <html>
        <body>
            <h2>Carpool Swap Request {status.capitalize()}</h2>
            <p>Hello,</p>
            <p>{responder_name} has {status} your carpool swap request for {formatted_date}.</p>
            <p>{'The schedule has been updated accordingly.' if accepted else 'Your original assignment remains unchanged.'}</p>
            <p>Please login to the Carpool Management App to view the details.</p>
            <p>Thank you for your participation in our carpool program.</p>
            <p>Best regards,<br>Carpool Management System</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Carpool Swap Request {status.capitalize()}
        
        Hello,
        
        {responder_name} has {status} your carpool swap request for {formatted_date}.
        
        {'The schedule has been updated accordingly.' if accepted else 'Your original assignment remains unchanged.'}
        
        Please login to the Carpool Management App to view the details.
        
        Thank you for your participation in our carpool program.
        
        Best regards,
        Carpool Management System
        """
        
        return self.send_email(to_email, subject, html_body, text_body)

# Create a singleton instance
email_service = EmailService()
