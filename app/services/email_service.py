from flask import current_app
from flask_mail import Message
from threading import Thread

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        from app import mail
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_email(to, subject, template, **kwargs):
    """Send email with template"""
    from app import mail
    
    msg = Message(
        subject=subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Send asynchronously to avoid blocking
    thr = Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
    thr.start()
    return thr

def send_application_confirmation(user_email, job_title, company_name):
    """Send application confirmation email"""
    if not current_app.config.get('MAIL_USERNAME'):
        # Email not configured, skip sending
        print(f"Email not configured - would send confirmation to {user_email}")
        return
    
    subject = f"Application Confirmation - {job_title}"
    
    html_template = f"""
    <html>
    <body>
        <h2>Application Confirmed</h2>
        <p>Dear Applicant,</p>
        <p>Thank you for applying to the position of <strong>{job_title}</strong> at <strong>{company_name}</strong>.</p>
        <p>We have received your application and will review it shortly.</p>
        <p>Best regards,<br>The Job Matching Team</p>
    </body>
    </html>
    """
    
    send_email(user_email, subject, html_template)

def send_status_update_email(user_email, job_title, company_name, status):
    """Send application status update email"""
    if not current_app.config.get('MAIL_USERNAME'):
        # Email not configured, skip sending
        print(f"Email not configured - would send status update to {user_email}")
        return
    
    subject = f"Application Update - {job_title}"
    
    status_messages = {
        'reviewing': 'Your application is being reviewed',
        'shortlisted': 'Congratulations! You have been shortlisted',
        'rejected': 'Thank you for your interest. We have decided to move forward with other candidates',
        'accepted': 'Congratulations! Your application has been accepted'
    }
    
    message = status_messages.get(status, f'Your application status has been updated to: {status}')
    
    html_template = f"""
    <html>
    <body>
        <h2>Application Status Update</h2>
        <p>Dear Applicant,</p>
        <p>We have an update regarding your application for <strong>{job_title}</strong> at <strong>{company_name}</strong>.</p>
        <p><strong>Status:</strong> {message}</p>
        <p>Best regards,<br>The Job Matching Team</p>
    </body>
    </html>
    """
    
    send_email(user_email, subject, html_template)