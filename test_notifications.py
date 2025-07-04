import os
from dotenv import load_dotenv

load_dotenv()

# Test Twilio setup
print("Testing notification setup...")
print(f"Twilio Account SID: {os.environ.get('TWILIO_ACCOUNT_SID', 'Not set')}")
print(f"Twilio Phone: {os.environ.get('TWILIO_PHONE_NUMBER', 'Not set')}")

# Test sending a notification
from app.services.notification_service import notification_service

# Replace with your phone number for testing
test_phone = "+254XXXXXXXXX"  # Your phone number with country code

# Test SMS
success = notification_service.send_sms(
    test_phone, 
    "Test SMS from Job Matching Platform"
)
print(f"SMS test: {'Success' if success else 'Failed'}")

# Test WhatsApp (requires WhatsApp sandbox setup)
success = notification_service.send_whatsapp(
    test_phone,
    "Test WhatsApp message from Job Matching Platform"
)
print(f"WhatsApp test: {'Success' if success else 'Failed'}")
