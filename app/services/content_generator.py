import os
from ai_models.train_models import ContentGenerator

# Load the trained model
model_path = os.environ.get('CONTENT_GENERATOR_MODEL_PATH', 'ai_models/saved/content_generator.pkl')
try:
    content_generator = ContentGenerator.load(model_path)
except:
    content_generator = ContentGenerator()

def generate_cover_letter(user, job):
    """Generate personalized cover letter"""
    user_profile = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'skills': user.profile.skills if user.profile else [],
        'experience_years': user.profile.experience_years if user.profile else 0
    }
    
    job_data = {
        'title': job.title,
        'skills_required': job.skills_required
    }
    
    company_data = {
        'name': job.company.name if job.company else 'your company'
    }
    
    return content_generator.generate_cover_letter(user_profile, job_data, company_data)

def generate_interview_prep(job):
    """Generate interview preparation content"""
    questions = content_generator.generate_interview_questions(job.to_dict())
    
    # Add tips based on job type
    tips = []
    
    if job.job_type == 'technical':
        tips.extend([
            "Prepare to discuss your technical projects in detail",
            "Be ready to solve coding problems on a whiteboard",
            "Review fundamental concepts related to the required skills",
            "Prepare questions about the tech stack and development process"
        ])
    else:
        tips.extend([
            "Research the company's mission and values",
            "Prepare specific examples demonstrating required skills",
            "Practice the STAR method for behavioral questions",
            "Prepare thoughtful questions about the role and team"
        ])
    
    return {
        'questions': questions,
        'tips': tips,
        'job_title': job.title,
        'company_name': job.company.name if job.company else 'the company'
    }
