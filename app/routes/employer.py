from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.job import Job, Company
from app.models.application import Application
from app.utils.decorators import employer_required

bp = Blueprint('employer', __name__)

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@employer_required()
def employer_dashboard():
    """Get employer dashboard data"""
    user_id = get_jwt_identity()
    
    # Get employer's jobs
    jobs = Job.query.filter_by(posted_by=user_id).all()
    
    # Calculate statistics
    total_jobs = len(jobs)
    active_jobs = len([j for j in jobs if j.is_active])
    
    # Get applications for employer's jobs
    job_ids = [j.id for j in jobs]
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []
    
    # Application statistics
    total_applications = len(applications)
    pending_applications = len([a for a in applications if a.status == 'pending'])
    
    # Get recent applications
    recent_applications = sorted(applications, key=lambda x: x.applied_at, reverse=True)[:10]
    
    return jsonify({
        'statistics': {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'pending_applications': pending_applications
        },
        'recent_applications': [app.to_dict() for app in recent_applications]
    }), 200

@bp.route('/jobs', methods=['GET'])
@jwt_required()
@employer_required()
def get_employer_jobs():
    """Get all jobs posted by employer"""
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    jobs_query = Job.query.filter_by(posted_by=user_id).order_by(Job.posted_date.desc())
    paginated = jobs_query.paginate(page=page, per_page=per_page, error_out=False)
    
    jobs = [job.to_dict() for job in paginated.items]
    
    # Add application count for each job
    for job in jobs:
        job['application_count'] = Application.query.filter_by(job_id=job['id']).count()
    
    return jsonify({
        'jobs': jobs,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@bp.route('/jobs/<int:job_id>/applications', methods=['GET'])
@jwt_required()
@employer_required()
def get_job_applications(job_id):
    """Get all applications for a specific job"""
    user_id = get_jwt_identity()
    
    # Verify job belongs to employer
    job = Job.query.get(job_id)
    if not job or job.posted_by != user_id:
        return jsonify({'error': 'Job not found or unauthorized'}), 404
    
    # Get applications
    status_filter = request.args.get('status')
    query = Application.query.filter_by(job_id=job_id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    applications = query.order_by(Application.match_score.desc()).all()
    
    # Include user info in response
    application_data = []
    for app in applications:
        app_dict = app.to_dict()
        user = User.query.get(app.user_id)
        app_dict['applicant'] = {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'profile': user.profile.to_dict() if user.profile else None
        }
        application_data.append(app_dict)
    
    return jsonify({
        'job': job.to_dict(),
        'applications': application_data,
        'total': len(application_data)
    }), 200

@bp.route('/applications/<int:application_id>/status', methods=['PUT'])
@jwt_required()
@employer_required()
def update_application_status(application_id):
    """Update application status"""
    user_id = get_jwt_identity()
    
    application = Application.query.get(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify the application is for employer's job
    job = Job.query.get(application.job_id)
    if job.posted_by != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    valid_statuses = ['pending', 'reviewing', 'shortlisted', 'rejected', 'accepted']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
    
    application.status = new_status
    db.session.commit()
    
    # Send notification email
    try:
        from app.services.email_service import send_status_update
        applicant = User.query.get(application.user_id)
        send_status_update(applicant.email, job.title, job.company.name, new_status)
    except:
        pass  # Email failed but status was updated
    
    return jsonify({
        'message': 'Application status updated',
        'application': application.to_dict()
    }), 200

@bp.route('/company', methods=['GET', 'PUT'])
@jwt_required()
@employer_required()
def manage_company():
    """Get or update company information"""
    user_id = get_jwt_identity()
    
    if request.method == 'GET':
        # Get employer's company
        jobs = Job.query.filter_by(posted_by=user_id).first()
        if jobs and jobs.company:
            return jsonify(jobs.company.to_dict()), 200
        else:
            return jsonify({'message': 'No company found'}), 404
    
    else:  # PUT
        data = request.get_json()
        
        # Find or create company
        company_name = data.get('name')
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        company = Company.query.filter_by(name=company_name).first()
        if not company:
            company = Company(name=company_name)
            db.session.add(company)
        
        # Update company details
        if 'description' in data:
            company.description = data['description']
        if 'industry' in data:
            company.industry = data['industry']
        if 'size' in data:
            company.size = data['size']
        if 'location' in data:
            company.location = data['location']
        if 'website' in data:
            company.website = data['website']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Company updated successfully',
            'company': company.to_dict()
        }), 200

@bp.route('/analytics', methods=['GET'])
@jwt_required()
@employer_required()
def get_analytics():
    """Get detailed analytics for employer"""
    user_id = get_jwt_identity()
    
    # Get all employer's jobs
    jobs = Job.query.filter_by(posted_by=user_id).all()
    job_ids = [j.id for j in jobs]
    
    if not job_ids:
        return jsonify({
            'total_jobs': 0,
            'total_applications': 0,
            'average_match_score': 0,
            'skill_demand': [],
            'application_timeline': []
        }), 200
    
    # Get all applications
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all()
    
    # Calculate metrics
    total_applications = len(applications)
    avg_match_score = sum(a.match_score for a in applications if a.match_score) / len(applications) if applications else 0
    
    # Status breakdown
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
    
    # Skill demand (most required skills across jobs)
    skill_counts = {}
    for job in jobs:
        if job.skills_required:
            for skill in job.skills_required:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Application timeline (last 30 days)
    from datetime import datetime, timedelta
    timeline = {}
    for i in range(30):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        timeline[str(date)] = 0
    
    for app in applications:
        if app.applied_at:
            date = app.applied_at.date()
            if str(date) in timeline:
                timeline[str(date)] += 1
    
    return jsonify({
        'total_jobs': len(jobs),
        'active_jobs': len([j for j in jobs if j.is_active]),
        'total_applications': total_applications,
        'average_match_score': round(avg_match_score, 1),
        'status_breakdown': status_counts,
        'top_skills': [{'skill': skill, 'count': count} for skill, count in top_skills],
        'application_timeline': [{'date': date, 'count': count} for date, count in sorted(timeline.items())]
    }), 200
