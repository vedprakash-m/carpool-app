import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.services.email_service import EmailService

class TestEmailService(unittest.TestCase):
    
    def setUp(self):
        # Create a mock settings object
        self.mock_settings_patcher = patch('app.services.email_service.settings')
        self.mock_settings = self.mock_settings_patcher.start()
        
        # Configure the mock settings
        self.mock_settings.SMTP_SERVER = 'smtp.example.com'
        self.mock_settings.SMTP_PORT = 587
        self.mock_settings.SMTP_USERNAME = 'test@example.com'
        self.mock_settings.SMTP_PASSWORD = 'password'
        self.mock_settings.FROM_EMAIL = 'noreply@carpoolapp.com'
        self.mock_settings.EMAIL_NOTIFICATIONS_ENABLED = True
        
        # Create the email service
        self.email_service = EmailService()
    
    def tearDown(self):
        self.mock_settings_patcher.stop()
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        # Setup
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test
        result = self.email_service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body_html='<p>Test HTML Body</p>',
            body_text='Test Plain Text Body'
        )
        
        # Verify
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.example.com', 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with('test@example.com', 'password')
        mock_smtp_instance.send_message.assert_called_once()
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_email_with_error(self, mock_smtp):
        # Setup - make the SMTP connection raise an exception
        mock_smtp.side_effect = Exception("Connection failed")
        
        # Test
        result = self.email_service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body_html='<p>Test HTML Body</p>'
        )
        
        # Verify
        self.assertFalse(result)  # Should return False on error
    
    def test_email_notifications_disabled(self):
        # Setup - disable email notifications
        self.mock_settings.EMAIL_NOTIFICATIONS_ENABLED = False
        
        # Test
        result = self.email_service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body_html='<p>Test HTML Body</p>'
        )
        
        # Verify
        self.assertFalse(result)  # Should return False when disabled
    
    @patch('app.services.email_service.EmailService.send_email')
    def test_send_swap_request_created_notification(self, mock_send_email):
        # Setup
        mock_send_email.return_value = True
        test_date = datetime.now()
        
        # Test
        result = self.email_service.send_swap_request_created_notification(
            to_email='driver@example.com',
            requester_name='John Doe',
            ride_date=test_date
        )
        
        # Verify
        self.assertTrue(result)
        mock_send_email.assert_called_once()
        # Check that both HTML and plain text versions are included
        html_body = mock_send_email.call_args[1]['body_html']
        text_body = mock_send_email.call_args[1]['body_text']
        self.assertIn('John Doe', html_body)  # Verify requester name in HTML
        self.assertIn('John Doe', text_body)  # Verify requester name in plain text
    
    @patch('app.services.email_service.EmailService.send_email')
    def test_send_swap_request_response_notification_accepted(self, mock_send_email):
        # Setup
        mock_send_email.return_value = True
        test_date = datetime.now()
        
        # Test
        result = self.email_service.send_swap_request_response_notification(
            to_email='requester@example.com',
            responder_name='Jane Smith',
            ride_date=test_date,
            accepted=True
        )
        
        # Verify
        self.assertTrue(result)
        mock_send_email.assert_called_once()
        # Check that acceptance message is included
        html_body = mock_send_email.call_args[1]['body_html']
        text_body = mock_send_email.call_args[1]['body_text']
        self.assertIn('accepted', html_body.lower())
        self.assertIn('schedule has been updated', html_body)
    
    @patch('app.services.email_service.EmailService.send_email')
    def test_send_swap_request_response_notification_rejected(self, mock_send_email):
        # Setup
        mock_send_email.return_value = True
        test_date = datetime.now()
        
        # Test
        result = self.email_service.send_swap_request_response_notification(
            to_email='requester@example.com',
            responder_name='Jane Smith',
            ride_date=test_date,
            accepted=False
        )
        
        # Verify
        self.assertTrue(result)
        mock_send_email.assert_called_once()
        # Check that rejection message is included
        html_body = mock_send_email.call_args[1]['body_html']
        text_body = mock_send_email.call_args[1]['body_text']
        self.assertIn('rejected', html_body.lower())
        self.assertIn('original assignment remains unchanged', html_body)

if __name__ == '__main__':
    unittest.main()
