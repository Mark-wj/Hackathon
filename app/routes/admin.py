from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db
from app.models.user import User, UserProfile
from app.models.job import Job, Company
from app.models.application import Application, MatchHistory
from app.utils.decorators import admin_required

bp = Blueprint('admin', __name__)

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required()
def admin_dashboard():
    """Get admin dashboard statistics"""
    
    # User statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    users_by_role = db.session.query(
        User.role, func.count(User.id)
    ).group_by(User.role).all()
    
    # Job statistics
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()
    
    # Application statistics
    total_applications = Application.query.count()
    applications_by_status = db.session.query(
        Application.status, func.count(Application.id)
    ).group_by(Application.status).all()
    
    # Company statistics
    total_companies = Company.query.count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.posted_date.desc()).limit(5).all()
    
    return jsonify({
        'statistics': {
            'users': {
                'total': total_users,
                'active': active_users,
                'by_role': dict(users_by_role)
            },
            'jobs': {
                'total': total_jobs,
                'active': active_jobs
            },
            'applications': {
                'total': total_applications,
                'by_status': dict(applications_by_status)
            },
            'companies': {
                'total': total_companies
            }
        },
        'recent_activity': {
            'users': [u.to_dict() for u in recent_users],
            'jobs': [j.to_dict() for j in recent_jobs]
        }
    }), 200

@bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_users():
    """Get all users with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    search = request.args.get('search')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    users = []
    for user in paginated.items:
        user_dict = user.to_dict()
        if user.profile:
            user_dict['profile_complete'] = bool(user.profile.skills and user.profile.location)
        else:
            user_dict['profile_complete'] = False
        users.append(user_dict)
    
    return jsonify({
        'users': users,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@bp.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@admin_required()
def manage_user(user_id):
    """Manage specific user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'GET':
        user_data = user.to_dict()
        if user.profile:
            user_data['profile'] = user.profile.to_dict()
        
        # Get user's applications
        applications = Application.query.filter_by(user_id=user_id).all()
        user_data['applications'] = [app.to_dict() for app in applications]
        
        return jsonify(user_data), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # Update user fields
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'role' in data and data['role'] in ['job_seeker', 'employer', 'admin']:
            user.role = data['role']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    
    else:  # DELETE
        # Soft delete - just deactivate
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'}), 200

@bp.route('/jobs', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_jobs():
    """Get all jobs for admin review"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')  # active, inactive
    
    query = Job.query
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    paginated = query.order_by(Job.posted_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    jobs = []
    for job in paginated.items:
        job_dict = job.to_dict()
        job_dict['application_count'] = Application.query.filter_by(job_id=job.id).count()
        job_dict['posted_by_email'] = User.query.get(job.posted_by).email if job.posted_by else None
        jobs.append(job_dict)
    
    return jsonify({
        'jobs': jobs,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@bp.route('/jobs/<int:job_id>/moderate', methods=['PUT'])
@jwt_required()
@admin_required()
def moderate_job(job_id):
    """Moderate job listing (activate/deactivate)"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    data = request.get_json()
    action = data.get('action')  # 'approve', 'reject', 'deactivate'
    reason = data.get('reason')
    
    if action == 'approve':
        job.is_active = True
    elif action in ['reject', 'deactivate']:
        job.is_active = False
    else:
        return jsonify({'error': 'Invalid action'}), 400
    
    db.session.commit()
    
    # TODO: Send notification to employer about moderation action
    
    return jsonify({
        'message': f'Job {action}d successfully',
        'job': job.to_dict()
    }), 200

@bp.route('/analytics', methods=['GET'])
@jwt_required()
@admin_required()
def get_platform_analytics():
    """Get comprehensive platform analytics"""
    
    # Time range
    from datetime import datetime, timedelta
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # User growth
    user_growth = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(User.created_at >= start_date).group_by(func.date(User.created_at)).all()
    
    # Job posting trends
    job_trends = db.session.query(
        func.date(Job.posted_date),
        func.count(Job.id)
    ).filter(Job.posted_date >= start_date).group_by(func.date(Job.posted_date)).all()
    
    # Application trends
    app_trends = db.session.query(
        func.date(Application.applied_at),
        func.count(Application.id)
    ).filter(Application.applied_at >= start_date).group_by(func.date(Application.applied_at)).all()
    
    # Top skills in demand
    all_skills = db.session.query(Job.skills_required).filter(Job.is_active==True).all()
    skill_counts = {}
    for skills in all_skills:
        if skills[0]:
            for skill in skills[0]:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    
    # Success metrics
    total_matches = MatchHistory.query.count()
    high_matches = MatchHistory.query.filter(MatchHistory.match_score >= 70).count()
    success_rate = (high_matches / total_matches * 100) if total_matches > 0 else 0
    
    return jsonify({
        'user_growth': [{'date': str(date), 'count': count} for date, count in user_growth],
        'job_trends': [{'date': str(date), 'count': count} for date, count in job_trends],
        'application_trends': [{'date': str(date), 'count': count} for date, count in app_trends],
        'top_skills': [{'skill': skill, 'count': count} for skill, count in top_skills],
        'success_metrics': {
            'total_matches': total_matches,
            'high_quality_matches': high_matches,
            'success_rate': round(success_rate, 1)
        }
    }), 200

@bp.route('/system/config', methods=['GET', 'PUT'])
@jwt_required()
@admin_required()
def system_config():
    """Get or update system configuration"""
    if request.method == 'GET':
        # Return current configuration (non-sensitive)
        return jsonify({
            'max_file_size': '16MB',
            'allowed_file_types': ['pdf', 'doc', 'docx', 'txt'],
            'rate_limits': {
                'default': '200 per day, 50 per hour'
            },
            'ai_models': {
                'resume_parser': 'active',
                'job_matcher': 'active',
                'content_generator': 'active'
            }
        }), 200
    
    else:  # PUT
        # Update configuration
        data = request.get_json()
        # TODO: Implement configuration updates
        return jsonify({'message': 'Configuration updated'}), 200
