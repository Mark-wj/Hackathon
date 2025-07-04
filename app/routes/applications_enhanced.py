from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.services.content_generator import generate_cover_letter
from app.services.email_service_enhanced import (
    send_application_documents, send_offer_letter, 
    send_rejection_email, send_email_async
)
from app.services.notification_service import send_application_status_notification
from app.services.document_service import document_service

bp = Blueprint('applications', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
def create_application():
    """Apply to a job with CV and cover letter processing"""
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
    
    # Process documents for employer
    try:
        # Generate CV PDF
        cv_path = document_service.process_cv_for_employer(user_id, application.id)
        
        # Generate cover letter PDF
        cover_letter_path = document_service.generate_cover_letter_pdf(
            user_id, application.id, cover_letter
        )
        
        # Send documents to employer
        employer = User.query.get(job.posted_by)
        if employer and cv_path and cover_letter_path:
            documents = [
                {
                    'path': cv_path,
                    'filename': f'CV_{user.first_name}_{user.last_name}.pdf',
                    'content_type': 'application/pdf'
                },
                {
                    'path': cover_letter_path,
                    'filename': f'Cover_Letter_{user.first_name}_{user.last_name}.pdf',
                    'content_type': 'application/pdf'
                }
            ]
            
            send_application_documents(
                employer.email,
                f"{user.first_name} {user.last_name}",
                job.title,
                job.company.name,
                documents
            )
    except Exception as e:
        print(f"Document processing error: {e}")
    
    # Send notification to applicant
    if user.profile and user.profile.phone:
        send_application_status_notification.delay(
            user.profile.phone,
            user.first_name,
            job.title,
            'pending'
        )
    
    return jsonify({
        'message': 'Application submitted successfully',
        'application': application.to_dict()
    }), 201

@bp.route('/<int:application_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status():
    """Update application status with notifications"""
    user_id = get_jwt_identity()
    application_id = request.args.get('application_id')
    
    application = Application.query.get(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Check authorization
    job = Job.query.get(application.job_id)
    if job.posted_by != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    valid_statuses = ['pending', 'reviewing', 'shortlisted', 'rejected', 'accepted']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
    
    old_status = application.status
    application.status = new_status
    db.session.commit()
    
    # Get applicant details
    applicant = User.query.get(application.user_id)
    
    # Handle status-specific actions
    if new_status == 'accepted':
        # Generate or use custom offer letter
        if data.get('custom_offer_letter'):
            offer_letter_path = document_service.generate_offer_letter(
                application.id, 
                custom_content=data.get('custom_offer_letter')
            )
        else:
            offer_letter_path = document_service.generate_offer_letter(application.id)
        
        # Send offer letter via email
        if offer_letter_path:
            send_offer_letter(
                applicant.email,
                applicant.first_name,
                job.title,
                job.company.name,
                offer_letter_path
            )
    
    elif new_status == 'rejected':
        # Send rejection email
        send_rejection_email(
            applicant.email,
            applicant.first_name,
            job.title,
            job.company.name
        )
    
    # Send SMS/WhatsApp notification
    if applicant.profile and applicant.profile.phone:
        send_application_status_notification.delay(
            applicant.profile.phone,
            applicant.first_name,
            job.title,
            new_status
        )
    
    return jsonify({
        'message': 'Application status updated',
        'application': application.to_dict()
    }), 200

@bp.route('/upload-offer-document', methods=['POST'])
@jwt_required()
def upload_offer_document():
    """Upload custom offer document"""
    user_id = get_jwt_identity()
    
    if 'document' not in request.files:
        return jsonify({'error': 'No document provided'}), 400
    
    file = request.files['document']
    application_id = request.form.get('application_id')
    
    if not application_id:
        return jsonify({'error': 'application_id required'}), 400
    
    application = Application.query.get(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify authorization
    job = Job.query.get(application.job_id)
    if job.posted_by != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Save the uploaded document
    filename = f"Custom_Offer_{application_id}_{file.filename}"
    filepath = os.path.join('generated_documents', filename)
    file.save(filepath)
    
    # Send to applicant
    applicant = User.query.get(application.user_id)
    send_offer_letter(
        applicant.email,
        applicant.first_name,
        job.title,
        job.company.name,
        filepath
    )
    
    return jsonify({'message': 'Offer document uploaded and sent'}), 200
