import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PyPDF2 import PdfReader, PdfWriter
import shutil
from datetime import datetime

class DocumentService:
    def __init__(self):
        self.upload_dir = 'uploads'
        self.output_dir = 'generated_documents'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_cv_for_employer(self, user_id, application_id):
        """Process user's CV for sending to employer"""
        from app.models.user import User
        user = User.query.get(user_id)
        
        if not user or not user.profile or not user.profile.resume_file_path:
            return None
        
        # Copy CV to a new location with application ID
        original_path = user.profile.resume_file_path
        if not os.path.exists(original_path):
            return None
        
        filename = f"CV_Application_{application_id}_{user.first_name}_{user.last_name}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        # If it's already a PDF, just copy it
        if original_path.endswith('.pdf'):
            shutil.copy(original_path, output_path)
        else:
            # Convert to PDF if needed (simplified - in production use proper converters)
            self.create_pdf_from_text(original_path, output_path)
        
        return output_path
    
    def generate_cover_letter_pdf(self, user_id, application_id, cover_letter_text):
        """Generate PDF version of cover letter"""
        from app.models.user import User
        from app.models.application import Application
        
        user = User.query.get(user_id)
        application = Application.query.get(application_id)
        
        filename = f"Cover_Letter_Application_{application_id}_{user.first_name}_{user.last_name}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add date
        date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], alignment=2)
        story.append(Paragraph(datetime.now().strftime("%B %d, %Y"), date_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Add cover letter content
        for paragraph in cover_letter_text.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        return output_path
    
    def generate_offer_letter(self, application_id, custom_content=None):
        """Generate offer letter PDF"""
        from app.models.application import Application
        from app.models.user import User
        
        application = Application.query.get(application_id)
        if not application:
            return None
        
        user = User.query.get(application.user_id)
        job = application.job
        company = job.company
        
        filename = f"Offer_Letter_{application_id}_{user.first_name}_{user.last_name}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading1'], alignment=1)
        story.append(Paragraph(f"{company.name}", header_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Date
        story.append(Paragraph(datetime.now().strftime("%B %d, %Y"), styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Recipient
        story.append(Paragraph(f"{user.first_name} {user.last_name}", styles['Normal']))
        if user.profile and user.profile.location:
            story.append(Paragraph(user.profile.location, styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Content
        if custom_content:
            content = custom_content
        else:
            content = f"""
Dear {user.first_name},

We are pleased to offer you the position of {job.title} at {company.name}. After reviewing your application and qualifications, we believe you will be a valuable addition to our team.

Position Details:
- Job Title: {job.title}
- Department: {job.job_type}
- Location: {job.location}
- Start Date: To be discussed

Compensation:
- Annual Salary: ${job.salary_min:,} - ${job.salary_max:,}
- Benefits: Health insurance, paid time off, and other standard benefits

This offer is contingent upon successful completion of our standard background check and reference verification.

Please confirm your acceptance of this offer by replying to this email within 5 business days.

We look forward to welcoming you to the {company.name} team!

Sincerely,

HR Department
{company.name}
            """
        
        for paragraph in content.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        return output_path
    
    def create_pdf_from_text(self, text_path, pdf_path):
        """Simple text to PDF conversion"""
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        for paragraph in text.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)

# Create singleton instance
document_service = DocumentService()
