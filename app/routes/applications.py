from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.services.job_matcher import calculate_match_score  # FIXED: This import should work now
from app.services.content_generator import generate_cover_letter
from app import db
from datetime import datetime

bp = Blueprint('applications', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_applications():
    """Get user's job applications"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        applications = user.applications.all()
        
        app_data = []
        for app in applications:
            app_dict = app.to_dict()
            app_data.append(app_dict)
        
        return jsonify({
            'applications': app_data,
            'total': len(app_data)
        }), 200
    except Exception as e:
        print(f"❌ Error getting applications: {str(e)}")
        return jsonify({'error': 'Failed to retrieve applications'}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_application():
    """Create a new job application"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.profile:
        return jsonify({'error': 'Please complete your profile first'}), 400
    
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if user already applied to this job
        existing_app = Application.query.filter_by(
            user_id=user_id, 
            job_id=job_id
        ).first()
        
        if existing_app:
            return jsonify({'error': 'You have already applied to this job'}), 400
        
        # Calculate match score using the fixed function
        try:
            match_score = calculate_match_score(user.profile.to_dict(), job.to_dict())
            print(f"✅ Calculated match score: {match_score}")
        except Exception as e:
            print(f"❌ Error calculating match score: {str(e)}")
            match_score = 0.0  # Default score if calculation fails
        
        # Generate cover letter if requested
        cover_letter = data.get('cover_letter', '')
        if data.get('generate_cover_letter', False):
            try:
                cover_letter = generate_cover_letter(user, job)
                print(f"✅ AI generated cover letter for {job.title}")
            except Exception as e:
                print(f"❌ Error generating cover letter: {str(e)}")
                cover_letter = f"Dear Hiring Manager,\n\nI am writing to express my interest in the {job.title} position at {job.company.name if job.company else 'your company'}.\n\nBest regards,\n{user.first_name} {user.last_name}"
        
        # Create application
        application = Application(
            user_id=user_id,
            job_id=job_id,
            cover_letter=cover_letter,
            match_score=match_score,
            status='pending'
        )
        
        db.session.add(application)
        db.session.commit()
        
        print(f"✅ Application created successfully for job: {job.title}")
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating application: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': 'Failed to create application'}), 500

@bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """Get a specific application"""
    user_id = get_jwt_identity()
    
    application = Application.query.filter_by(
        id=application_id,
        user_id=user_id
    ).first()
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    return jsonify(application.to_dict()), 200

@bp.route('/<int:application_id>', methods=['PUT'])
@jwt_required()
def update_application(application_id):
    """Update an application (e.g., cover letter)"""
    user_id = get_jwt_identity()
    
    application = Application.query.filter_by(
        id=application_id,
        user_id=user_id
    ).first()
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Don't allow updates to submitted applications
    if application.status != 'pending':
        return jsonify({'error': 'Cannot update submitted application'}), 400
    
    try:
        data = request.get_json()
        
        if 'cover_letter' in data:
            application.cover_letter = data['cover_letter']
        
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Application updated successfully',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        print(f"❌ Error updating application: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update application'}), 500

@bp.route('/<int:application_id>', methods=['DELETE'])
@jwt_required()
def delete_application(application_id):
    """Delete an application"""
    user_id = get_jwt_identity()
    
    application = Application.query.filter_by(
        id=application_id,
        user_id=user_id
    ).first()
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Don't allow deletion of submitted applications
    if application.status not in ['pending', 'draft']:
        return jsonify({'error': 'Cannot delete submitted application'}), 400
    
    try:
        db.session.delete(application)
        db.session.commit()
        
        return jsonify({'message': 'Application deleted successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error deleting application: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete application'}), 500