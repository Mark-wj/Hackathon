from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.job import Job
from app.services.job_matcher import find_best_matches
from app.services.content_generator import generate_interview_prep
from app.services.resume_parser import extract_skills

bp = Blueprint('ai', __name__)

@bp.route('/match-jobs', methods=['POST'])
@jwt_required()
def match_jobs():
    """Find best job matches for user"""
    user_id = get_jwt_identity()
    print(f"DEBUG: match_jobs called for user_id: {user_id}")
    
    user = User.query.get(user_id)
    if not user:
        print(f"DEBUG: User {user_id} not found")
        return jsonify({'error': 'User not found'}), 404
    
    print(f"DEBUG: User found: {user.email}")
    print(f"DEBUG: Has profile: {user.profile is not None}")
    
    if user.profile:
        print(f"DEBUG: Profile skills: {user.profile.skills}")
        print(f"DEBUG: Profile location: {user.profile.location}")
    
    if not user.profile or not user.profile.skills:
        print(f"DEBUG: Profile incomplete - profile: {user.profile}, skills: {user.profile.skills if user.profile else 'No profile'}")
        return jsonify({'error': 'Please complete your profile with skills first'}), 400
    
    data = request.get_json() or {}
    
    # Get filter parameters
    location = data.get('location', user.profile.location)
    job_type = data.get('job_type')
    min_match_score = data.get('min_match_score', 50)
    
    print(f"DEBUG: Finding matches with min_score: {min_match_score}")
    
    # Find matches
    try:
        matches = find_best_matches(user, location=location, job_type=job_type,
                                   min_score=min_match_score)
        print(f"DEBUG: Found {len(matches)} matches")
        
        return jsonify({
            'matches': matches[:20],  # Return top 20 matches
            'total_matches': len(matches)
        }), 200
    except Exception as e:
        print(f"DEBUG: Error in find_best_matches: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/generate-cover-letter', methods=['POST'])
@jwt_required()
def generate_cover_letter_api():
    """Generate cover letter for a specific job"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.profile:
        return jsonify({'error': 'Please complete your profile first'}), 400
    
    data = request.get_json()
    job_id = data.get('job_id')
    
    if not job_id:
        return jsonify({'error': 'job_id is required'}), 400
    
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Generate cover letter
    from app.services.content_generator import generate_cover_letter
    cover_letter = generate_cover_letter(user, job)
    
    return jsonify({
        'cover_letter': cover_letter,
        'job_title': job.title,
        'company_name': job.company.name
    }), 200

@bp.route('/interview-prep/<int:job_id>', methods=['GET'])
@jwt_required()
def get_interview_prep(job_id):
    """Get interview preparation for a job"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Generate interview questions and tips
    prep_data = generate_interview_prep(job)
    
    return jsonify(prep_data), 200

@bp.route('/extract-skills', methods=['POST'])
@jwt_required()
def extract_skills_from_text():
    """Extract skills from text"""
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'text is required'}), 400
    
    skills = extract_skills(text)
    
    return jsonify({
        'skills': skills,
        'count': len(skills)
    }), 200

@bp.route('/analyze-profile', methods=['GET'])
@jwt_required()
def analyze_profile():
    """Analyze user profile completeness and suggestions"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    analysis = {
        'profile_completeness': 0,
        'missing_fields': [],
        'suggestions': []
    }
    
    # Check profile completeness
    total_fields = 0
    completed_fields = 0
    
    # Basic user info
    fields_to_check = {
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
    
    # Profile fields
    if user.profile:
        fields_to_check.update({
            'phone': user.profile.phone,
            'location': user.profile.location,
            'summary': user.profile.summary,
            'skills': user.profile.skills,
            'experience_years': user.profile.experience_years,
            'education': user.profile.education,
            'work_experience': user.profile.work_experience
        })
    
    for field, value in fields_to_check.items():
        total_fields += 1
        if value:
            completed_fields += 1
        else:
            analysis['missing_fields'].append(field)
    
    analysis['profile_completeness'] = int((completed_fields / total_fields) * 100)
    
    # Suggestions
    if 'skills' in analysis['missing_fields']:
        analysis['suggestions'].append('Add your skills to get better job matches')
    if 'summary' in analysis['missing_fields']:
        analysis['suggestions'].append('Add a professional summary to stand out')
    if 'location' in analysis['missing_fields']:
        analysis['suggestions'].append('Add your location to find relevant jobs')
    
    return jsonify(analysis), 200
