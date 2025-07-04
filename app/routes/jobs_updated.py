from app.services.auto_matcher import trigger_job_matching

# Update the create_job function to trigger matching
@bp.route('/', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new
cat >> app/routes/jobs_updated.py << 'EOF'
   """Create a new job posting with auto-matching"""
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
   
   # Trigger auto-matching for this job
   trigger_job_matching(job)
   
   return jsonify({
       'message': 'Job created successfully',
       'job': job.to_dict()
   }), 201
