from flask_mail import Message
from app import mail, celery
import os

@celery.task
def send_email_async(subject, recipient, body, html_body=None, attachments=None):
    """Send email asynchronously"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            html=html_body
        )
        
        # Add attachments if any
        if attachments:
            for attachment in attachments:
                with open(attachment['path'], 'rb') as f:
                    msg.attach(
                        attachment['filename'],
                        attachment['content_type'],
                        f.read()
                    )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_verification_email(email, token):
    """Send email verification link"""
    verification_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:5000')}/verify-email/{token}"
    
    subject = "Verify your email - Job Matching Platform"
    body = f"""
    Welcome to Job Matching Platform!
    
    Please verify your email by clicking the link below:
    {verification_url}
    
    This link will expire in 24 hours.
    
    Best regards,
    Job Matching Platform Team
    """
    
    html_body = f"""
    <h2>Welcome to Job Matching Platform!</h2>
    <p>Please verify your email by clicking the link below:</p>
    <p><a href="{verification_url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
    <p>Or copy and paste this link: {verification_url}</p>
    <p>This link will expire in 24 hours.</p>
    <br>
    <p>Best regards,<br>Job Matching Platform Team</p>
    """
    
    send_email_async.delay(subject, email, body, html_body)

def send_application_documents(email, applicant_name, job_title, company_name, documents):
    """Send application documents to employer"""
    subject = f"New Application - {job_title} - {applicant_name}"
    
    body = f"""
    Dear Hiring Manager,
    
    You have received a new application for the {job_title} position.
    
    Applicant: {applicant_name}
    Email: {email}
    
    Please find the attached CV and cover letter.
    
    Best regards,
    Job Matching Platform
    """
    
    send_email_async.delay(subject, email, body, attachments=documents)

def send_offer_letter(email, applicant_name, job_title, company_name, offer_letter_path):
    """Send offer letter to accepted candidate"""
    subject = f"Congratulations! Job Offer - {job_title} at {company_name}"
    
    body = f"""
    Dear {applicant_name},
    
    Congratulations! We are pleased to offer you the position of {job_title} at {company_name}.
    
    Please find your offer letter attached. We look forward to welcoming you to our team!
    
    Best regards,
    {company_name} HR Team
    """
    
    attachments = [{
        'path': offer_letter_path,
        'filename': f'Offer_Letter_{job_title.replace(" ", "_")}.pdf',
        'content_type': 'application/pdf'
    }]
    
    send_email_async.delay(subject, email, body, attachments=attachments)

def send_rejection_email(email, applicant_name, job_title, company_name):
    """Send rejection email to candidate"""
    subject = f"Application Update - {job_title} at {company_name}"
    
    body = f"""
    Dear {applicant_name},
    
    Thank you for your interest in the {job_title} position at {company_name}.
    
    After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.
    
    We appreciate the time you took to apply and encourage you to apply for future opportunities that match your skills and experience.
    
    We wish you the best in your job search.
    
    Best regards,
    {company_name} HR Team
    """
    
    send_email_async.delay(subject, email, body)
