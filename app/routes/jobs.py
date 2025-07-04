from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app import db
from app.models.job import Job, Company
from app.models.user import User
from app.models.application import MatchHistory

bp = Blueprint('jobs', __name__)

@bp.route('/search', methods=['GET'])
def search_jobs():
    """Search for jobs"""
    # Get search parameters
    query = request.args.get('q', '')
    location = request.args.get('location')
    job_type = request.args.get('job_type')
    experience_level = request.args.get('experience_level')
    is_remote = request.args.get('is_remote', type=bool)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    jobs_query = Job.query.filter_by(is_active=True)
    
    if query:
        search_filter = or_(
            Job.title.ilike(f'%{query}%'),
            Job.description.ilike(f'%{query}%'),
            Job.requirements.ilike(f'%{query}%')
        )
        jobs_query = jobs_query.filter(search_filter)
    
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f'%{location}%'))
    
    if job_type:
        jobs_query = jobs_query.filter_by(job_type=job_type)
    
    if experience_level:
        jobs_query = jobs_query.filter_by(experience_level=experience_level)
    
    if is_remote:
        jobs_query = jobs_query.filter_by(is_remote=True)
    
    # Paginate results
    paginated = jobs_query.paginate(page=page, per_page=per_page, error_out=False)
    
    jobs = [job.to_dict() for job in paginated.items]
    
    return jsonify({
        'jobs': jobs,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details"""
    job = Job.query.get(job_id)
    
    if not job or not job.is_active:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job.to_dict()), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job posting (for employers)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # For testing, allow any user to create jobs
    # In production, check if user.role == 'employer'
    
    data = request.get_json()
    
    # Create company if not exists
    company_name = data.get('company_name', 'Tech Company')
    company = Company.query.filter_by(name=company_name).first()
    if not company:
        company = Company(
            name=company_name,
            description=data.get('company_description', 'A great tech company'),
            industry=data.get('company_industry', 'Technology'),
            size=data.get('company_size', '50-200'),
            location=data.get('company_location', 'Nairobi, Kenya')
        )
        db.session.add(company)
        db.session.flush()
    
    # Create job
    job = Job(
        posted_by=user_id,
        company_id=company.id,
        title=data.get('title', 'Software Developer'),
        description=data.get('description', 'We are looking for a talented developer'),
        requirements=data.get('requirements', 'Bachelor degree in Computer Science'),
        skills_required=data.get('skills_required', ['python', 'flask']),
        experience_level=data.get('experience_level', 'mid'),
        job_type=data.get('job_type', 'full_time'),
        location=data.get('location', 'Nairobi, Kenya'),
        salary_min=data.get('salary_min', 50000),
        salary_max=data.get('salary_max', 100000),
        is_remote=data.get('is_remote', False)
    )
    
    db.session.add(job)
    db.session.commit()
    
    return jsonify({
        'message': 'Job created successfully',
        'job': job.to_dict()
    }), 201

@bp.route('/<int:job_id>/match', methods=['GET'])
@jwt_required()
def get_job_match(job_id):
    """Get match score for current user and specific job"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    job = Job.query.get(job_id)
    
    if not user or not job:
        return jsonify({'error': 'User or job not found'}), 404
    
    if not user.profile or not user.profile.skills:
        return jsonify({'error': 'Please complete your profile first'}), 400
    
    # Calculate match score
    from app.services.job_matcher import calculate_match_score
    
    user_profile_dict = user.profile.to_dict()
    job_dict = job.to_dict()
    
    scores = calculate_match_score(user_profile_dict, job_dict)
    
    # Save to match history
    match_history = MatchHistory(
        user_id=user.id,
        job_id=job.id,
        match_score=scores['overall'],
        skill_match_score=scores['skill_match'],
        experience_match_score=scores['experience_match'],
        location_match_score=scores['location_match']
    )
    db.session.add(match_history)
    db.session.commit()
    
    return jsonify({
        'job': job_dict,
        'scores': scores,
        'recommendation': 'Strong match!' if scores['overall'] > 70 else 'Good match' if scores['overall'] > 50 else 'Fair match'
    }), 200
