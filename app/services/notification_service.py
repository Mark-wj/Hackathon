import os
from twilio.rest import Client
from app import celery
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        self.twilio_whatsapp_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')
        
        if self.twilio_account_sid and self.twilio_auth_token:
            self.client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured")
    
    def send_sms(self, to_number, message):
        """Send SMS notification"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=to_number
            )
            logger.info(f"SMS sent successfully: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_whatsapp(self, to_number, message):
        """Send WhatsApp notification"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            # WhatsApp numbers need 'whatsapp:' prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            message = self.client.messages.create(
                body=message,
                from_=f'whatsapp:{self.twilio_whatsapp_number}',
                to=to_number
            )
            logger.info(f"WhatsApp message sent successfully: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp: {str(e)}")
            return False

# Create singleton instance
notification_service = NotificationService()

@celery.task
def send_application_status_notification(phone_number, applicant_name, job_title, status):
    """Send notification about application status change"""
    messages = {
        'reviewing': f"Hi {applicant_name}, your application for {job_title} is now being reviewed.",
        'shortlisted': f"Congratulations {applicant_name}! You've been shortlisted for {job_title}.",
        'rejected': f"Hi {applicant_name}, unfortunately your application for {job_title} was not successful. Keep applying!",
        'accepted': f"🎉 Congratulations {applicant_name}! You've been accepted for {job_title}! Check your email for the offer letter."
    }
    
    message = messages.get(status, f"Your application status for {job_title} has been updated to: {status}")
    
    # Send both SMS and WhatsApp
    notification_service.send_sms(phone_number, message)
    notification_service.send_whatsapp(phone_number, message)

@celery.task
def send_new_job_match_notification(phone_number, user_name, job_title, match_score):
    """Notify user about new job match"""
    message = f"Hi {user_name}, we found a new job match for you! {job_title} with {match_score:.0f}% match score. Login to apply!"
    
    notification_service.send_sms(phone_number, message)
    notification_service.send_whatsapp(phone_number, message)
