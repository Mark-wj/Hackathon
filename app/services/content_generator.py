import os
import pickle

# Load the actual AI models
def load_ai_models():
    """Load the trained AI models"""
    models = {}
    model_dir = 'ai_models/saved'
    
    try:
        # Load ContentGenerator
        generator_path = os.path.join(model_dir, 'content_generator.pkl')
        if os.path.exists(generator_path):
            with open(generator_path, 'rb') as f:
                models['content_generator'] = pickle.load(f)
        
        print(f"✅ Content AI models loaded: {list(models.keys())}")
        return models
    except Exception as e:
        print(f"❌ Error loading content AI models: {str(e)}")
        return {}

# Global models instance
CONTENT_AI_MODELS = load_ai_models()

def get_content_generator():
    """Get the AI content generator"""
    return CONTENT_AI_MODELS.get('content_generator')

def generate_cover_letter(user, job):
    """Generate cover letter using AI model"""
    generator = get_content_generator()
    
    if generator:
        # Use the actual AI model
        try:
            # Prepare user profile data
            user_profile = {
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'skills': user.profile.skills if user.profile else [],
                'experience_years': user.profile.experience_years if user.profile else 0,
            }
            
            # Prepare job data
            job_data = {
                'title': job.title,
                'skills_required': job.skills_required or [],
                'description': job.description
            }
            
            # Prepare company data
            company_data = {
                'name': job.company.name if job.company else 'the company'
            }
            
            cover_letter = generator.generate_cover_letter(user_profile, job_data, company_data)
            print(f"✅ AI generated cover letter for {job.title}")
            return cover_letter
            
        except Exception as e:
            print(f"❌ AI cover letter generation error: {str(e)}")
            return generate_cover_letter_basic(user, job)
    else:
        # Use basic generation if AI model not available
        print("⚠️ Using basic cover letter generation (AI model not loaded)")
        return generate_cover_letter_basic(user, job)

def generate_cover_letter_basic(user, job):
    """Basic cover letter generation fallback"""
    user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not user_name:
        user_name = "Candidate"
    
    job_title = job.title
    company_name = job.company.name if job.company else "your company"
    
    # Get user skills that match job requirements
    user_skills = user.profile.skills if user.profile else []
    job_skills = job.skills_required or []
    matching_skills = [s for s in user_skills if s.lower() in [j.lower() for j in job_skills]]
    
    skills_text = ', '.join(matching_skills[:3]) if matching_skills else 'relevant technical skills'
    experience_years = user.profile.experience_years if user.profile else 'several'
    
    cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With {experience_years} years of experience in technology, I am confident that my skills and background make me an ideal candidate for this role.

My technical expertise includes {skills_text}, which aligns perfectly with your requirements. I have successfully applied these skills in previous roles to deliver high-quality solutions and improve team productivity.

In my previous role, I led successful projects and improved processes. This experience has prepared me well for the challenges and responsibilities of the {job_title} position.

I am particularly drawn to {company_name} because of your innovative approach and commitment to excellence. I believe my {skills_text} would contribute significantly to your team's success.

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {company_name}.

Sincerely,
{user_name}"""
    
    return cover_letter.strip()

def generate_interview_prep(job):
    """Generate interview preparation using AI model"""
    generator = get_content_generator()
    
    if generator:
        # Use the actual AI model
        try:
            # Prepare job data
            job_data = {
                'title': job.title,
                'skills_required': job.skills_required or [],
                'description': job.description,
                'company': job.company.name if job.company else 'the company'
            }
            
            questions = generator.generate_interview_questions(job_data)
            
            prep_data = {
                'questions': questions,
                'tips': generate_interview_tips(job),
                'key_topics': job.skills_required[:5] if job.skills_required else []
            }
            
            print(f"✅ AI generated interview prep for {job.title}")
            return prep_data
            
        except Exception as e:
            print(f"❌ AI interview prep generation error: {str(e)}")
            return generate_interview_prep_basic(job)
    else:
        # Use basic generation if AI model not available
        print("⚠️ Using basic interview prep generation (AI model not loaded)")
        return generate_interview_prep_basic(job)

def generate_interview_prep_basic(job):
    """Basic interview preparation fallback"""
    questions = []
    
    # Technical questions based on required skills
    for skill in (job.skills_required or [])[:3]:
        questions.extend([
            f"Can you describe your experience with {skill}?",
            f"What projects have you worked on using {skill}?",
            f"How do you stay updated with {skill} best practices?"
        ])
    
    # General questions
    questions.extend([
        f"Why are you interested in the {job.title} position?",
        "Tell me about a challenging project you've worked on.",
        "How do you handle working under pressure?",
        "Describe a time when you had to learn a new technology quickly.",
        "What are your career goals for the next 5 years?",
        "How do you approach problem-solving?",
        "Tell me about a time you worked in a team.",
        "What interests you about our company?"
    ])
    
    return {
        'questions': questions,
        'tips': generate_interview_tips(job),
        'key_topics': job.skills_required[:5] if job.skills_required else []
    }

def generate_interview_tips(job):
    """Generate interview tips"""
    tips = [
        "Research the company thoroughly before the interview",
        "Prepare specific examples of your work and achievements",
        "Practice explaining technical concepts in simple terms",
        "Prepare questions to ask the interviewer",
        "Review your resume and be ready to discuss any experience mentioned"
    ]
    
    # Add skill-specific tips
    skills = job.skills_required or []
    if 'python' in [s.lower() for s in skills]:
        tips.append("Be ready to discuss Python projects and coding best practices")
    if 'react' in [s.lower() for s in skills]:
        tips.append("Prepare to discuss React components, state management, and modern practices")
    if any('data' in s.lower() for s in skills):
        tips.append("Be ready to discuss data analysis methodologies and tools")
    
    return tips

def generate_application_email(user, job, cover_letter=None):
    """Generate professional application email"""
    user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not user_name:
        user_name = "Candidate"
    
    subject = f"Application for {job.title} Position - {user_name}"
    
    if not cover_letter:
        cover_letter = generate_cover_letter(user, job)
    
    email_body = f"""Subject: {subject}

{cover_letter}

Please find my resume attached for your review.

Best regards,
{user_name}"""
    
    return {
        'subject': subject,
        'body': email_body,
        'cover_letter': cover_letter
    }

def generate_follow_up_email(user, job, application_date):
    """Generate follow-up email template"""
    user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not user_name:
        user_name = "Candidate"
    
    company_name = job.company.name if job.company else "your company"
    
    subject = f"Follow-up on {job.title} Application - {user_name}"
    
    body = f"""Subject: {subject}

Dear Hiring Manager,

I hope this email finds you well. I wanted to follow up on my application for the {job.title} position at {company_name}, which I submitted on {application_date}.

I remain very interested in this opportunity and believe my skills and experience would be a valuable addition to your team. I would welcome the chance to discuss how I can contribute to {company_name}'s continued success.

Please let me know if you need any additional information from me. I look forward to hearing from you.

Best regards,
{user_name}"""
    
    return {
        'subject': subject,
        'body': body
    }

def reload_content_ai_models():
    """Reload AI models (useful for updates)"""
    global CONTENT_AI_MODELS
    CONTENT_AI_MODELS = load_ai_models()
    return CONTENT_AI_MODELS

# Initialize models on import
if not CONTENT_AI_MODELS:
    print("🔄 No content AI models found. Run 'python ai_models/train_models.py' to train models.")