import os
from app import db
from app.models.job import Job
from app.models.application import MatchHistory

def calculate_match_score(user_profile, job):
    """Calculate match score between user and job"""
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
    
    # Location matching - case insensitive
    user_location = user_profile.get('location', '').lower()
    job_location = job.get('location', '').lower()
    
    if job.get('is_remote') or user_location == job_location:
        location_match = 1.0
    elif user_location and job_location:
        # Check if any part of user location is in job location
        location_match = 0.8 if any(word in job_location for word in user_location.split()) else 0.3
    else:
        location_match = 0.3
    
    scores['location_match'] = location_match * 100
    
    # Overall score (weighted average)
    overall_score = (
        scores['skill_match'] * 0.5 +
        scores['experience_match'] * 0.3 +
        scores['location_match'] * 0.2
    )
    
    scores['overall'] = overall_score
    
    return scores

def match_user_to_jobs(user, jobs):
    """Match user to multiple jobs"""
    if not user.profile:
        return []
    
    user_profile = user.profile.to_dict()
    results = []
    
    for job in jobs:
        scores = calculate_match_score(user_profile, job.to_dict())
        
        # Save match history
        match_history = MatchHistory(
            user_id=user.id,
            job_id=job.id,
            match_score=scores['overall'],
            skill_match_score=scores['skill_match'],
            experience_match_score=scores['experience_match'],
            location_match_score=scores['location_match']
        )
        db.session.add(match_history)
        
        results.append({
            'job': job.to_dict(),
            'scores': scores
        })
    
    db.session.commit()
    return results

def find_best_matches(user, location=None, job_type=None, min_score=50):
    """Find best job matches for user"""
    # Get active jobs
    query = Job.query.filter_by(is_active=True)
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    if job_type:
        query = query.filter_by(job_type=job_type)
    
    jobs = query.all()
    
    # Get matches
    matches = match_user_to_jobs(user, jobs)
    
    # Filter by minimum score
    filtered_matches = [m for m in matches if m['scores']['overall'] >= min_score]
    
    # Sort by score
    filtered_matches.sort(key=lambda x: x['scores']['overall'], reverse=True)
    
    return filtered_matches

# Try to load the AI model, but fall back to the simple implementation
try:
    from ai_models.train_models import JobMatcher
    model_path = os.environ.get('JOB_MATCHER_MODEL_PATH', 'ai_models/saved/job_matcher.pkl')
    job_matcher = JobMatcher.load(model_path) if os.path.exists(model_path) else None
except:
    job_matcher = None
