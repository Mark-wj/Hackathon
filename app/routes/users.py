from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.user import User, UserProfile
from app.services.resume_parser import parse_resume_file
from app.config import Config

bp = Blueprint('users', __name__)

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile_data = user.to_dict()
    if user.profile:
        profile_data['profile'] = user.profile.to_dict()
    
    return jsonify(profile_data), 200

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update user info
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    # Update profile
    profile = user.profile
    if not profile:
        profile = UserProfile(user=user)
        db.session.add(profile)
    
    # Update profile fields
    profile_fields = ['phone', 'location', 'summary', 'skills', 'experience_years',
                     'education', 'work_experience', 'linkedin_url', 'github_url', 'portfolio_url']
    
    for field in profile_fields:
        if field in data:
            setattr(profile, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict(),
        'profile': profile.to_dict()
    }), 200

@bp.route('/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    """Upload and parse resume"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if 'resume' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    allowed_extensions = Config.ALLOWED_EXTENSIONS
    if not any(file.filename.endswith(ext) for ext in allowed_extensions):
        return jsonify({'error': f'Invalid file type. Allowed: {allowed_extensions}'}), 400
    
    # Save file
    filename = secure_filename(f"resume_{user_id}_{file.filename}")
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(filepath)
    
    # Parse resume
    try:
        parsed_data = parse_resume_file(filepath)
        
        # Update user profile with parsed data
        profile = user.profile
        if not profile:
            profile = UserProfile(user=user)
            db.session.add(profile)
        
        profile.resume_file_path = filepath
        if parsed_data.get('skills'):
            profile.skills = parsed_data['skills']
        if parsed_data.get('summary'):
            profile.summary = parsed_data['summary']
        if parsed_data.get('education'):
            profile.education = {'items': parsed_data['education']}
        if parsed_data.get('experience'):
            profile.work_experience = {'items': parsed_data['experience']}
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resume uploaded and parsed successfully',
            'parsed_data': parsed_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to parse resume: {str(e)}'}), 500
