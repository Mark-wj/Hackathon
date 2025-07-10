import os
import pickle
import pdfplumber
from docx import Document

# Load the actual AI models
def load_ai_models():
    """Load the trained AI models"""
    models = {}
    model_dir = 'ai_models/saved'
    
    try:
        # Load ResumeParser
        parser_path = os.path.join(model_dir, 'resume_parser.pkl')
        if os.path.exists(parser_path):
            with open(parser_path, 'rb') as f:
                models['resume_parser'] = pickle.load(f)
        
        # Load SkillExtractor
        skill_path = os.path.join(model_dir, 'skill_extractor.pkl')
        if os.path.exists(skill_path):
            with open(skill_path, 'rb') as f:
                models['skill_extractor'] = pickle.load(f)
        
        print(f"✅ Resume AI models loaded: {list(models.keys())}")
        return models
    except Exception as e:
        print(f"❌ Error loading resume AI models: {str(e)}")
        return {}

# Global models instance
RESUME_AI_MODELS = load_ai_models()

def get_resume_parser():
    """Get the AI resume parser"""
    return RESUME_AI_MODELS.get('resume_parser')

def get_skill_extractor():
    """Get the AI skill extractor"""
    return RESUME_AI_MODELS.get('skill_extractor')

def extract_text_from_file(filepath):
    """Extract text from various file formats"""
    try:
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            text = ""
            try:
                with pdfplumber.open(filepath) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
            except Exception as e:
                print(f"❌ PDF parsing error: {str(e)}")
                return ""
        
        elif ext in ['.doc', '.docx']:
            try:
                doc = Document(filepath)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except Exception as e:
                print(f"❌ DOCX parsing error: {str(e)}")
                return ""
        
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    except Exception as e:
        print(f"❌ File extraction error: {str(e)}")
        return ""

def parse_resume_file(filepath):
    """Parse resume from file using AI models"""
    # Extract text from file
    text = extract_text_from_file(filepath)
    if not text.strip():
        return {
            'error': 'Could not extract text from file',
            'skills': [],
            'education': [],
            'experience': [],
            'contact': {},
            'summary': ''
        }
    
    # Parse using AI model
    return parse_resume_text(text)

def parse_resume_text(text):
    """Parse resume text using AI models"""
    parser = get_resume_parser()
    
    if parser:
        # Use the actual AI model
        try:
            result = parser.parse_resume(text)
            print(f"✅ AI parsed resume - found {len(result.get('skills', []))} skills")
            return result
        except Exception as e:
            print(f"❌ AI parsing error: {str(e)}")
            # Fall back to basic parsing
            return parse_resume_basic(text)
    else:
        # Use basic parsing if AI model not available
        print("⚠️ Using basic resume parsing (AI model not loaded)")
        return parse_resume_basic(text)

def parse_resume_basic(text):
    """Basic resume parsing fallback"""
    # Extract skills using basic method
    skills = extract_skills(text)
    
    # Basic information extraction
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Try to find email and phone
    contact = {}
    import re
    
    # Email regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact['email'] = emails[0]
    
    # Phone regex
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phones = re.findall(phone_pattern, text)
    if phones:
        contact['phone'] = phones[0]
    
    # Basic education detection
    education = []
    education_keywords = ['university', 'college', 'school', 'degree', 'bachelor', 'master', 'phd', 'diploma']
    for line in lines:
        if any(keyword in line.lower() for keyword in education_keywords):
            education.append(line)
    
    # Basic experience detection
    experience = []
    experience_keywords = ['experience', 'worked', 'position', 'role', 'job', 'company', 'employed']
    for line in lines:
        if any(keyword in line.lower() for keyword in experience_keywords):
            experience.append(line)
    
    return {
        'skills': skills,
        'education': education,
        'experience': experience,
        'contact': contact,
        'summary': ' '.join(lines[:3])  # First 3 lines as summary
    }

def extract_skills(text):
    """Extract skills from text using AI or fallback"""
    skill_extractor = get_skill_extractor()
    
    if skill_extractor:
        # Use AI skill extractor
        try:
            skills = skill_extractor.extract_skills(text)
            print(f"✅ AI extracted {len(skills)} skills")
            return skills
        except Exception as e:
            print(f"❌ AI skill extraction error: {str(e)}")
            return extract_skills_basic(text)
    else:
        # Use basic skill extraction
        print("⚠️ Using basic skill extraction (AI model not loaded)")
        return extract_skills_basic(text)

def extract_skills_basic(text):
    """Basic skill extraction fallback"""
    text_lower = text.lower()
    
    # Comprehensive tech skills list
    tech_skills = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',
        
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'jquery', 'bootstrap', 'tailwind css',
        'node.js', 'express', 'django', 'flask', 'spring', 'laravel', 'rails',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite',
        'oracle', 'sql server', 'cassandra',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'gitlab',
        'github', 'terraform', 'ansible', 'circleci',
        
        # Data Science & AI
        'machine learning', 'deep learning', 'data science', 'artificial intelligence',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'jupyter', 'spark', 'hadoop',
        
        # Mobile
        'android', 'ios', 'react native', 'flutter', 'xamarin',
        
        # Other
        'agile', 'scrum', 'microservices', 'rest api', 'graphql', 'websockets'
    ]
    
    # Soft skills
    soft_skills = [
        'communication', 'leadership', 'teamwork', 'problem solving',
        'critical thinking', 'creativity', 'adaptability', 'time management',
        'project management', 'analytical', 'detail oriented'
    ]
    
    all_skills = tech_skills + soft_skills
    found_skills = []
    
    for skill in all_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates

def analyze_resume_completeness(parsed_resume):
    """Analyze how complete a resume is"""
    score = 0
    total_fields = 5
    
    if parsed_resume.get('skills'):
        score += 1
    if parsed_resume.get('contact'):
        score += 1
    if parsed_resume.get('experience'):
        score += 1
    if parsed_resume.get('education'):
        score += 1
    if parsed_resume.get('summary'):
        score += 1
    
    completeness = (score / total_fields) * 100
    return {
        'completeness_score': completeness,
        'missing_sections': get_missing_sections(parsed_resume)
    }

def get_missing_sections(parsed_resume):
    """Get list of missing resume sections"""
    missing = []
    
    if not parsed_resume.get('skills'):
        missing.append('skills')
    if not parsed_resume.get('contact'):
        missing.append('contact_information')
    if not parsed_resume.get('experience'):
        missing.append('work_experience')
    if not parsed_resume.get('education'):
        missing.append('education')
    if not parsed_resume.get('summary'):
        missing.append('professional_summary')
    
    return missing

def reload_resume_ai_models():
    """Reload AI models (useful for updates)"""
    global RESUME_AI_MODELS
    RESUME_AI_MODELS = load_ai_models()
    return RESUME_AI_MODELS

# Initialize models on import
if not RESUME_AI_MODELS:
    print("🔄 No resume AI models found. Run 'python ai_models/train_models.py' to train models.")