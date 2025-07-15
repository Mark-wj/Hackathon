from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

def get_current_user():
    """Get current authenticated user"""
    from app.models.user import User  # Import here to avoid circular import
    current_user_id = get_jwt_identity()
    if current_user_id:
        return User.query.get(current_user_id)
    return None

@dashboard_bp.route('/dashboard/stats')
@jwt_required()
def dashboard_stats():
    """Get dashboard statistics based on user role"""
    from app.models.user import User
    from app.models.job import Job
    from app.models.application import Application
    from app import db
    
    user = get_current_user()
    
    if user.role == 'job_seeker':
        # Job seeker stats
        applications_count = Application.query.filter_by(user_id=user.id).count()
        pending_applications = Application.query.filter_by(user_id=user.id, status='pending').count()
        interview_applications = Application.query.filter_by(user_id=user.id, status='interview').count()
        
        return jsonify({
            'role': 'job_seeker',
            'stats': {
                'applications': applications_count,
                'pending': pending_applications,
                'interviews': interview_applications,
                'profile_completeness': calculate_profile_completeness(user)
            }
        })
    
    elif user.role == 'employer':
        # Employer stats
        posted_jobs = Job.query.filter_by(posted_by=user.id).count()
        active_jobs = Job.query.filter_by(posted_by=user.id, is_active=True).count()
        total_applications = db.session.query(func.count(Application.id)).join(Job).filter(Job.posted_by == user.id).scalar()
        pending_applications = db.session.query(func.count(Application.id)).join(Job).filter(Job.posted_by == user.id, Application.status == 'pending').scalar()
        
        return jsonify({
            'role': 'employer',
            'stats': {
                'total_jobs': posted_jobs,
                'active_jobs': active_jobs,
                'total_applications': total_applications or 0,
                'pending_applications': pending_applications or 0
            }
        })
    
    elif user.role == 'admin':
        # Admin stats
        total_users = User.query.count()
        active_jobs = Job.query.filter_by(is_active=True).count()
        total_applications = Application.query.count()
        
        return jsonify({
            'role': 'admin',
            'stats': {
                'total_users': total_users,
                'active_jobs': active_jobs,
                'total_applications': total_applications,
                'total_companies': 0,  # Add if you have companies
                'success_rate': 12  # Calculate based on your logic
            }
        })

def calculate_profile_completeness(user):
    """Calculate profile completeness percentage"""
    if not user.profile:
        return 0
    
    profile = user.profile
    total_fields = 10
    completed_fields = 0
    
    if profile.phone: completed_fields += 1
    if profile.location: completed_fields += 1
    if profile.summary: completed_fields += 1
    if profile.skills: completed_fields += 1
    if profile.experience_years: completed_fields += 1
    if profile.education: completed_fields += 1
    if profile.work_experience: completed_fields += 1
    if profile.linkedin_url: completed_fields += 1
    if profile.github_url: completed_fields += 1
    if profile.portfolio_url: completed_fields += 1
    
    return int((completed_fields / total_fields) * 100)

@dashboard_bp.route('/dashboard/recent-activity')
@jwt_required()
def recent_activity():
    """Get recent activity based on user role"""
    from app.models.application import Application
    from app.models.job import Job
    
    user = get_current_user()
    
    if user.role == 'job_seeker':
        # Recent applications
        recent_apps = Application.query.filter_by(user_id=user.id).order_by(Application.applied_at.desc()).limit(5).all()
        
        activities = []
        for app in recent_apps:
            activities.append({
                'type': 'application',
                'message': f'Applied to {app.job.title}',
                'timestamp': app.applied_at.isoformat() if app.applied_at else None,
                'status': app.status
            })
        
        return jsonify({'activities': activities})
    
    elif user.role == 'employer':
        # Recent applications to employer's jobs
        from app import db
        recent_apps = db.session.query(Application).join(Job).filter(
            Job.posted_by == user.id
        ).order_by(Application.created_at.desc()).limit(5).all()
        
        activities = []
        for app in recent_apps:
            activities.append({
                'type': 'application_received',
                'message': f'New application for {app.job.title}',
                'timestamp': app.created_at.isoformat(),
                'status': app.status
            })
        
        return jsonify({'activities': activities})
    
    elif user.role == 'admin':
        # Recent platform activity
        from app.models.user import User
        recent_users = User.query.order_by(User.created_at.desc()).limit(3).all()
        
        activities = []
        for user_obj in recent_users:
            activities.append({
                'type': 'user_registration',
                'message': f'New user registered: {user_obj.email}',
                'timestamp': user_obj.created_at.isoformat(),
                'role': user_obj.role
            })
        
        return jsonify({'activities': activities})
    
    return jsonify({'activities': []})

@dashboard_bp.route('/dashboard/recommendations')
@jwt_required()
def job_recommendations():
    """Get job recommendations for job seekers"""
    from app.models.job import Job
    
    user = get_current_user()
    
    if user.role != 'job_seeker':
        return jsonify({'error': 'Only job seekers can get recommendations'}), 403
    
    if not user.profile or not user.profile.skills:
        return jsonify({'recommendations': []})
    
    user_skills = user.profile.skills
    
    # Simple recommendation - get active jobs
    # In a real implementation, you'd use your AI matching algorithms
    recommended_jobs = Job.query.filter(Job.is_active == True).limit(5).all()
    
    recommendations = []
    for job in recommended_jobs:
        # Calculate simple match percentage
        if job.skills_required and user_skills:
            matching_skills = set(user_skills) & set(job.skills_required)
            match_percentage = (len(matching_skills) / len(job.skills_required)) * 100
        else:
            match_percentage = 50  # Default match
        
        recommendations.append({
            'job_id': job.id,
            'title': job.title,
            'company': job.company.name if job.company else 'N/A',
            'location': job.location,
            'match_percentage': int(match_percentage),
            'salary_range': f"${job.salary_min}-${job.salary_max}" if job.salary_min and job.salary_max else None,
            'job_type': job.job_type,
            'posted_date': job.posted_date.isoformat() if job.posted_date else None
        })
    
    return jsonify({'recommendations': recommendations})