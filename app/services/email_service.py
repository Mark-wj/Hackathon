from flask_mail import Message
from app import mail

def send_email(subject, recipient, body, html_body=None):
    """Send email"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_application_confirmation(user_email, job_title, company_name):
    """Send application confirmation email"""
    subject = f"Application Submitted - {job_title}"
    body = f"""
Dear Candidate,

Your application for the {job_title} position at {company_name} has been successfully submitted.

We'll notify you of any updates to your application status.

Best regards,
Job Matching Platform Team
"""
    
    return send_email(subject, user_email, body)

def send_status_update(user_email, job_title, company_name, new_status):
    """Send application status update"""
    subject = f"Application Status Update - {job_title}"
    
    status_messages = {
        'reviewing': "is currently being reviewed",
        'shortlisted': "has been shortlisted! You'll hear from the employer soon",
        'rejected': "has been reviewed and unfortunately, you were not selected",
        'accepted': "has been accepted! Congratulations!"
    }
    
    status_msg = status_messages.get(new_status, f"status has been updated to {new_status}")
    
    body = f"""
Dear Candidate,

Your application for the {job_title} position at {company_name} {status_msg}.

Best regards,
Job Matching Platform Team
"""
    
    return send_email(subject, user_email, body)
