from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.services.job_matcher import find_best_matches, reload_ai_models
from app.services.content_generator import generate_cover_letter, generate_interview_prep
from app.services.resume_parser import extract_skills, parse_resume_text, parse_resume_file
from app import db 
import os

bp = Blueprint('ai', __name__)

@bp.route('/match-jobs', methods=['POST'])
@jwt_required()
def match_jobs():
    """Find best job matches for user using AI"""
    user_id = get_jwt_identity()
    print(f"🔍 AI match_jobs called for user_id: {user_id}")
    
    user = User.query.get(user_id)
    if not user:
        print(f"❌ User {user_id} not found")
        return jsonify({'error': 'User not found'}), 404
    
    print(f"✅ User found: {user.email}")
    print(f"📋 Has profile: {user.profile is not None}")
    
    if user.profile:
        print(f"🎯 Profile skills: {user.profile.skills}")
        print(f"📍 Profile location: {user.profile.location}")
    
    if not user.profile or not user.profile.skills:
        print(f"⚠️ Profile incomplete - profile: {user.profile}, skills: {user.profile.skills if user.profile else 'No profile'}")
        return jsonify({'error': 'Please complete your profile with skills first'}), 400
    
    data = request.get_json() or {}
    
    # Get filter parameters
    location = data.get('location', user.profile.location)
    job_type = data.get('job_type')
    min_match_score = data.get('min_match_score', 50)
    
    print(f"🎯 Finding AI matches with min_score: {min_match_score}")
    
    # Find matches using AI
    try:
        matches = find_best_matches(user, location=location, job_type=job_type,
                                   min_score=min_match_score)
        print(f"✅ AI found {len(matches)} matches")
        
        return jsonify({
            'matches': matches[:20],  # Return top 20 matches
            'total_matches': len(matches),
            'ai_powered': True
        }), 200
    except Exception as e:
        print(f"❌ Error in AI find_best_matches: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/generate-cover-letter', methods=['POST'])
@jwt_required()
def generate_cover_letter_api():
    """Generate cover letter for a specific job using AI"""
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
    
    try:
        # Generate cover letter using AI
        cover_letter = generate_cover_letter(user, job)
        
        print(f"✅ AI generated cover letter for job: {job.title}")
        
        return jsonify({
            'cover_letter': cover_letter,
            'job_title': job.title,
            'company_name': job.company.name if job.company else 'Company',
            'ai_powered': True
        }), 200
    except Exception as e:
        print(f"❌ Error generating cover letter: {str(e)}")
        return jsonify({'error': 'Failed to generate cover letter'}), 500

@bp.route('/interview-prep/<int:job_id>', methods=['GET'])
@jwt_required()
def get_interview_prep(job_id):
    """Get AI-powered interview preparation for a job"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    try:
        # Generate interview questions and tips using AI
        prep_data = generate_interview_prep(job)
        prep_data['ai_powered'] = True
        
        print(f"✅ AI generated interview prep for: {job.title}")
        return jsonify(prep_data), 200
    except Exception as e:
        print(f"❌ Error generating interview prep: {str(e)}")
        return jsonify({'error': 'Failed to generate interview preparation'}), 500

@bp.route('/extract-skills', methods=['POST'])
@jwt_required()
def extract_skills_from_text():
    """Extract skills from text using AI"""
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'text is required'}), 400
    
    try:
        skills = extract_skills(text)
        
        print(f"✅ AI extracted {len(skills)} skills from text")
        
        return jsonify({
            'skills': skills,
            'count': len(skills),
            'ai_powered': True
        }), 200
    except Exception as e:
        print(f"❌ Error extracting skills: {str(e)}")
        return jsonify({'error': 'Failed to extract skills'}), 500

@bp.route('/parse-resume', methods=['POST'])
@jwt_required()
def parse_resume():
    """Parse resume file using AI"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save uploaded file temporarily
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        file.save(temp_path)
        
        # Parse using AI
        parsed_data = parse_resume_file(temp_path)
        parsed_data['ai_powered'] = True
        
        print(f"✅ AI parsed resume: {file.filename}")
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify(parsed_data), 200
    except Exception as e:
        print(f"❌ Error parsing resume: {str(e)}")
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': 'Failed to parse resume'}), 500

@bp.route('/parse-resume-text', methods=['POST'])
@jwt_required()
def parse_resume_text_api():
    """Parse resume from text using AI"""
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'text is required'}), 400
    
    try:
        parsed_data = parse_resume_text(text)
        parsed_data['ai_powered'] = True
        
        print(f"✅ AI parsed resume text")
        return jsonify(parsed_data), 200
    except Exception as e:
        print(f"❌ Error parsing resume text: {str(e)}")
        return jsonify({'error': 'Failed to parse resume text'}), 500

@bp.route('/analyze-profile', methods=['GET'])
@jwt_required()
def analyze_profile():
    """Analyze user profile completeness and provide AI suggestions"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    analysis = {
        'profile_completeness': 0,
        'missing_fields': [],
        'suggestions': [],
        'ai_powered': True
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
    
    # AI-powered suggestions
    if 'skills' in analysis['missing_fields']:
        analysis['suggestions'].append('🎯 Add your technical skills to get AI-powered job matches')
    if 'summary' in analysis['missing_fields']:
        analysis['suggestions'].append('📝 Add a professional summary to stand out to employers')
    if 'location' in analysis['missing_fields']:
        analysis['suggestions'].append('📍 Add your location to find relevant local and remote jobs')
    if 'experience_years' in analysis['missing_fields']:
        analysis['suggestions'].append('⏱️ Add your years of experience for better job matching')
    if 'work_experience' in analysis['missing_fields']:
        analysis['suggestions'].append('💼 Add your work experience for stronger applications')
    
    # Additional AI suggestions based on profile completeness
    if analysis['profile_completeness'] < 50:
        analysis['suggestions'].append('🚀 Complete your profile to unlock AI-powered features')
    elif analysis['profile_completeness'] < 80:
        analysis['suggestions'].append('⭐ You\'re almost there! Complete a few more fields for optimal results')
    else:
        analysis['suggestions'].append('✅ Great profile! You\'re ready for AI-powered job matching')
    
    print(f"📊 Profile analysis: {analysis['profile_completeness']}% complete")
    return jsonify(analysis), 200

@bp.route('/match-history', methods=['GET'])
@jwt_required()
def get_match_history():
    """Get user's AI match history"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # FIXED: Use proper SQLAlchemy query instead of trying to query on relationship
        matches = db.session.query(MatchHistory).filter(
            MatchHistory.user_id == user_id
        ).order_by(MatchHistory.created_at.desc()).limit(50).all()
        
        match_data = []
        for match in matches:
            match_dict = match.to_dict()
            match_dict['ai_powered'] = True
            match_data.append(match_dict)
        
        return jsonify({
            'matches': match_data,
            'total': len(match_data),
            'ai_powered': True
        }), 200
    except Exception as e:
        print(f"❌ Error getting match history: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to retrieve match history'}), 500

@bp.route('/reload-models', methods=['POST'])
@jwt_required()
def reload_models():
    """Reload AI models (admin function)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Only allow admins to reload models
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Reload all AI models
        from app.services.job_matcher import reload_ai_models
        from app.services.resume_parser import reload_resume_ai_models
        from app.services.content_generator import reload_content_ai_models
        
        job_models = reload_ai_models()
        resume_models = reload_resume_ai_models()
        content_models = reload_content_ai_models()
        
        return jsonify({
            'message': 'AI models reloaded successfully',
            'loaded_models': {
                'job_matching': list(job_models.keys()),
                'resume_parsing': list(resume_models.keys()),
                'content_generation': list(content_models.keys())
            }
        }), 200
    except Exception as e:
        print(f"❌ Error reloading models: {str(e)}")
        return jsonify({'error': 'Failed to reload models'}), 500

@bp.route('/model-status', methods=['GET'])
@jwt_required()
def get_model_status():
    """Get status of AI models"""
    from app.services.job_matcher import AI_MODELS
    from app.services.resume_parser import RESUME_AI_MODELS
    from app.services.content_generator import CONTENT_AI_MODELS
    
    status = {
        'job_matching': {
            'loaded': len(AI_MODELS) > 0,
            'models': list(AI_MODELS.keys())
        },
        'resume_parsing': {
            'loaded': len(RESUME_AI_MODELS) > 0,
            'models': list(RESUME_AI_MODELS.keys())
        },
        'content_generation': {
            'loaded': len(CONTENT_AI_MODELS) > 0,
            'models': list(CONTENT_AI_MODELS.keys())
        }
    }
    
    return jsonify(status), 200