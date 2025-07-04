import os
import pickle
import sys
import nltk
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Download required NLTK data
print("Downloading NLTK data...")
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model loaded successfully")
except:
    print("Please run: python -m spacy download en_core_web_sm")
    sys.exit(1)

class SkillExtractor:
    """Extract skills from text using NLP"""
    
    def __init__(self):
        self.tech_skills = {
            'python', 'java', 'javascript', 'c++', 'sql', 'react', 'angular',
            'node.js', 'django', 'flask', 'machine learning', 'deep learning',
            'data science', 'aws', 'docker', 'kubernetes', 'git', 'agile',
            'html', 'css', 'mongodb', 'postgresql', 'mysql', 'redis',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'
        }
        
        self.soft_skills = {
            'communication', 'leadership', 'teamwork', 'problem solving',
            'critical thinking', 'creativity', 'adaptability', 'time management',
            'project management', 'analytical', 'detail oriented'
        }
        
        self.all_skills = self.tech_skills.union(self.soft_skills)
    
    def extract_skills(self, text):
        text = text.lower()
        doc = nlp(text)
        found_skills = []
        
        for skill in self.all_skills:
            if skill in text:
                found_skills.append(skill)
        
        return list(set(found_skills))
    
    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

class ResumeParser:
    """Parse and extract information from resumes"""
    
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def parse_resume(self, text):
        doc = nlp(text)
        
        info = {
            'skills': self.skill_extractor.extract_skills(text),
            'education': self._extract_education(doc),
            'experience': self._extract_experience(doc),
            'contact': self._extract_contact(text),
            'summary': self._extract_summary(text)
        }
        
        return info
    
    def _extract_education(self, doc):
        education = []
        education_keywords = ['university', 'college', 'school', 'degree', 'bachelor', 'master', 'phd']
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in education_keywords):
                education.append(sent.text.strip())
        
        return education
    
    def _extract_experience(self, doc):
        experience = []
        experience_keywords = ['experience', 'worked', 'position', 'role', 'job', 'company']
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in experience_keywords):
                experience.append(sent.text.strip())
        
        return experience
    
    def _extract_contact(self, text):
        contact = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact['phone'] = phones[0]
        
        return contact
    
    def _extract_summary(self, text):
        lines = text.split('\n')
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in summary_keywords):
                return ' '.join(lines[i:i+3])
        
        return ' '.join(lines[:3])
    
    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

class JobMatcher:
    """Match candidates to jobs using ML"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.skill_extractor = SkillExtractor()
    
    def calculate_match_score(self, user_profile, job):
        scores = {}
        
        # Skill matching
        user_skills = set(user_profile.get('skills', []))
        job_skills = set(job.get('skills_required', []))
        
        if job_skills:
            skill_match = len(user_skills.intersection(job_skills)) / len(job_skills)
        else:
            skill_match = 0.5
        
        scores['skill_match'] = skill_match * 100
        
        # Experience matching
        user_exp = user_profile.get('experience_years', 0)
        job_exp = job.get('experience_level', 'entry')
        
        exp_mapping = {'entry': 0, 'junior': 2, 'mid': 5, 'senior': 8, 'expert': 10}
        required_exp = exp_mapping.get(job_exp.lower(), 0)
        
        if user_exp >= required_exp:
            exp_match = 1.0
        else:
            exp_match = user_exp / (required_exp + 1)
        
        scores['experience_match'] = exp_match * 100
        
        # Location matching
        user_location = user_profile.get('location', '').lower()
        job_location = job.get('location', '').lower()
        
        if job.get('is_remote') or user_location == job_location:
            location_match = 1.0
        elif user_location and job_location:
            location_match = 0.5 if any(word in job_location for word in user_location.split()) else 0.2
        else:
            location_match = 0.3
        
        scores['location_match'] = location_match * 100
        
        # Overall score
        overall_score = (
            scores['skill_match'] * 0.5 +
            scores['experience_match'] * 0.3 +
            scores['location_match'] * 0.2
        )
        
        scores['overall'] = overall_score
        
        return scores
    
    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

class ContentGenerator:
    """Generate cover letters and application content"""
    
    def __init__(self):
        self.templates = {
            'cover_letter': """Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. 
With {experience_years} years of experience in {relevant_field}, I am confident that my 
skills and background make me an ideal candidate for this role.

{skill_paragraph}

{experience_paragraph}

I am particularly drawn to {company_name} because {company_reason}. I believe my 
{key_skills} would contribute significantly to your team's success.

Thank you for considering my application. I look forward to the opportunity to discuss 
how I can contribute to {company_name}.

Sincerely,
{user_name}""",
            'skill_paragraph': """My technical expertise includes {skills}, which aligns perfectly with your requirements. 
I have successfully applied these skills in previous roles to {achievements}.""",
            'experience_paragraph': """In my previous role at {previous_company}, I {key_achievement}. This experience has 
prepared me well for the challenges and responsibilities of the {job_title} position."""
        }
    
    def generate_cover_letter(self, user_profile, job, company):
        user_name = f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip()
        job_title = job.get('title', 'position')
        company_name = company.get('name', 'your company')
        
        user_skills = user_profile.get('skills', [])
        relevant_skills = [s for s in user_skills if s in job.get('skills_required', [])][:3]
        skills_str = ', '.join(relevant_skills) if relevant_skills else 'relevant technical skills'
        
        skill_para = self.templates['skill_paragraph'].format(
            skills=skills_str,
            achievements='deliver high-quality solutions and improve team productivity'
        )
        
        exp_para = self.templates['experience_paragraph'].format(
            previous_company='my previous company',
            key_achievement='led successful projects and improved processes',
            job_title=job_title
        )
        
        cover_letter = self.templates['cover_letter'].format(
            job_title=job_title,
            company_name=company_name,
            experience_years=user_profile.get('experience_years', 'several'),
            relevant_field='technology',
            skill_paragraph=skill_para,
            experience_paragraph=exp_para,
            company_reason='of your innovative approach and commitment to excellence',
            key_skills=skills_str,
            user_name=user_name if user_name else 'Candidate'
        )
        
        return cover_letter.strip()
    
    def generate_interview_questions(self, job):
        questions = []
        
        for skill in job.get('skills_required', [])[:3]:
            questions.append(f"Can you describe your experience with {skill}?")
            questions.append(f"What projects have you worked on using {skill}?")
        
        questions.extend([
            f"Why are you interested in the {job.get('title')} position?",
            "Tell me about a challenging project you've worked on.",
            "How do you stay updated with the latest technology trends?",
            "Describe a time when you had to work under pressure.",
            "What are your career goals for the next 5 years?"
        ])
        
        return questions
    
    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

# Training script
def train_and_save_models():
    """Train and save all AI models"""
    os.makedirs('ai_models/saved', exist_ok=True)
    
    print("Initializing models...")
    skill_extractor = SkillExtractor()
    resume_parser = ResumeParser()
    job_matcher = JobMatcher()
    content_generator = ContentGenerator()
    
    print("Saving models...")
    skill_extractor.save('ai_models/saved/skill_extractor.pkl')
    resume_parser.save('ai_models/saved/resume_parser.pkl')
    job_matcher.save('ai_models/saved/job_matcher.pkl')
    content_generator.save('ai_models/saved/content_generator.pkl')
    
    print("All models trained and saved successfully!")

if __name__ == "__main__":
    train_and_save_models()
