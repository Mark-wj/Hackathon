from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.services.content_generator import generate_cover_letter
from app.services.email_service import send_application_confirmation

bp = Blueprint('applications', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
def create_application():
    """Apply to a job"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    job_id = data.get('job_id')
    
    if not job_id:
        return jsonify({'error': 'job_id is required'}), 400
    
    job = Job.query.get(job_id)
    if not job or not job.is_active:
        return jsonify({'error': 'Job not found or inactive'}), 404
    
    # Check if already applied
    existing = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing:
        return jsonify({'error': 'Already applied to this job'}), 409
    
    # Generate cover letter if requested
    cover_letter = data.get('cover_letter')
    if data.get('generate_cover_letter'):
        if user.profile:
            cover_letter = generate_cover_letter(user, job)
        else:
            return jsonify({'error': 'Complete your profile to generate cover letter'}), 400
    
    # Create application
    application = Application(
        user_id=user_id,
        job_id=job_id,
        cover_letter=cover_letter,
        status='pending'
    )
    
    # Calculate match score
    if user.profile and user.profile.skills:
        from app.services.job_matcher import calculate_match_score
        scores = calculate_match_score(user.profile.to_dict(), job.to_dict())
        application.match_score = scores['overall']
    
    db.session.add(application)
    db.session.commit()
    
    # Send confirmation email (will fail silently if email not configured)
    try:
        send_application_confirmation(user.email, job.title, job.company.name)
    except:
        pass  # Email sending failed, but application was saved
    
    return jsonify({
        'message': 'Application submitted successfully',
        'application': application.to_dict()
    }), 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_my_applications():
    """Get current user's applications"""
    user_id = get_jwt_identity()
    
    # Get query parameters
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    query = Application.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    
    # Order by most recent first
    query = query.order_by(Application.applied_at.desc())
    
    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    applications = [app.to_dict() for app in paginated.items]
    
    return jsonify({
        'applications': applications,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """Get application details"""
    user_id = get_jwt_identity()
    application = Application.query.get(application_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Check authorization
    if application.user_id != user_id and application.job.posted_by != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(application.to_dict()), 200

@bp.route('/<int:application_id>', methods=['PUT'])
@jwt_required()
def update_application(application_id):
    """Update application (withdraw or update status)"""
    user_id = get_jwt_identity()
    application = Application.query.get(application_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    data = request.get_json()
    
    # Job seekers can only withdraw
    if application.user_id == user_id:
        if data.get('status') == 'withdrawn':
            application.status = 'withdrawn'
        else:
            return jsonify({'error': 'Can only withdraw application'}), 400
    
    # Employers can update status
    elif application.job.posted_by == user_id:
        if 'status' in data:
            valid_statuses = ['pending', 'reviewing', 'shortlisted', 'rejected', 'accepted']
            if data['status'] in valid_statuses:
                application.status = data['status']
                # Send status update email
                try:
                    from app.services.email_service import send_status_update
                    user = User.query.get(application.user_id)
                    send_status_update(user.email, application.job.title, 
                                     application.job.company.name, data['status'])
                except:
                    pass
            else:
                return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.commit()
    
    return jsonify({
        'message': 'Application updated successfully',
        'application': application.to_dict()
    }), 200

@bp.route('/status', methods=['GET'])
@jwt_required()
def get_application_status():
    """Get application status summary"""
    user_id = get_jwt_identity()
    
    # Get status counts
    from sqlalchemy import func
    status_counts = db.session.query(
        Application.status,
        func.count(Application.id)
    ).filter_by(user_id=user_id).group_by(Application.status).all()
    
    status_summary = {status: count for status, count in status_counts}
    
    return jsonify({
        'status_summary': status_summary,
        'total_applications': sum(status_summary.values())
    }), 200
