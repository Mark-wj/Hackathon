import os
import pickle
from app import db
from app.models.job import Job
from app.models.application import MatchHistory

# Load the actual AI models
def load_ai_models():
    """Load the trained AI models"""
    models = {}
    model_dir = 'ai_models/saved'
    
    try:
        # Load JobMatcher
        matcher_path = os.path.join(model_dir, 'job_matcher.pkl')
        if os.path.exists(matcher_path):
            with open(matcher_path, 'rb') as f:
                models['job_matcher'] = pickle.load(f)
        
        # Load SkillExtractor
        skill_path = os.path.join(model_dir, 'skill_extractor.pkl')
        if os.path.exists(skill_path):
            with open(skill_path, 'rb') as f:
                models['skill_extractor'] = pickle.load(f)
        
        print(f"✅ Loaded AI models: {list(models.keys())}")
        return models
    except Exception as e:
        print(f"❌ Error loading AI models: {str(e)}")
        return {}

# Global models instance
AI_MODELS = load_ai_models()

def get_job_matcher():
    """Get the AI job matcher or fallback to basic logic"""
    return AI_MODELS.get('job_matcher')

def calculate_match_score_ai(user_profile, job):
    """Calculate match score using AI model"""
    matcher = get_job_matcher()
    
    if matcher:
        # Use the actual AI model
        try:
            scores = matcher.calculate_match_score(user_profile, job)
            return scores
        except Exception as e:
            print(f"❌ AI matcher error: {str(e)}")
            # Fall back to basic logic
            return calculate_match_score_basic(user_profile, job)
    else:
        # Use basic logic if AI model not available
        return calculate_match_score_basic(user_profile, job)

def calculate_match_score_basic(user_profile, job):
    """Fallback basic match calculation"""
    scores = {}
    
    # Skill matching - case insensitive
    user_skills = set([s.lower() for s in user_profile.get('skills', [])])
    job_skills = set([s.lower() for s in job.get('skills_required', [])])
    
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
        location_match = 0.8 if any(word in job_location for word in user_location.split()) else 0.3
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

def calculate_match_score(user_profile, job_data):
    """
    Main function that other modules expect to import
    This returns the full scores dictionary, not just the overall score
    """
    # Call your existing AI function
    scores = calculate_match_score_ai(user_profile, job_data)
    
    # Return the full dictionary of scores (not just overall)
    return scores  # ✅ This returns the full dictionary

def match_user_to_jobs(user, jobs):
    """Match user to multiple jobs using AI"""
    if not user.profile:
        return []
    
    user_profile = user.profile.to_dict()
    results = []
    
    for job in jobs:
        job_dict = job.to_dict()
        scores = calculate_match_score_ai(user_profile, job_dict)
        
        # Save match history
        try:
            match_history = MatchHistory(
                user_id=user.id,
                job_id=job.id,
                match_score=scores['overall'],
                skill_match_score=scores['skill_match'],
                experience_match_score=scores['experience_match'],
                location_match_score=scores['location_match']
            )
            db.session.add(match_history)
        except Exception as e:
            print(f"❌ Error saving match history: {str(e)}")
        
        results.append({
            'job': job_dict,
            'scores': scores
        })
    
    try:
        db.session.commit()
    except Exception as e:
        print(f"❌ Error committing match history: {str(e)}")
        db.session.rollback()
    
    return results

def find_best_matches(user, location=None, job_type=None, min_score=50):
    """Find best job matches for user using AI"""
    # Get active jobs
    query = Job.query.filter_by(is_active=True)
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    if job_type:
        query = query.filter_by(job_type=job_type)
    
    jobs = query.all()
    print(f"📊 Found {len(jobs)} active jobs to match against")
    
    # Get matches using AI
    matches = match_user_to_jobs(user, jobs)
    print(f"🎯 Generated {len(matches)} job matches")
    
    # Filter by minimum score
    filtered_matches = [m for m in matches if m['scores']['overall'] >= min_score]
    print(f"✅ {len(filtered_matches)} matches above {min_score}% threshold")
    
    # Sort by score (highest first)
    filtered_matches.sort(key=lambda x: x['scores']['overall'], reverse=True)
    
    return filtered_matches

def reload_ai_models():
    """Reload AI models (useful for updates)"""
    global AI_MODELS
    AI_MODELS = load_ai_models()
    return AI_MODELS

# Initialize models on import
if not AI_MODELS:
    print("🔄 No AI models found. Run 'python ai_models/train_models.py' to train models.")