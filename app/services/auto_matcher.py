from app import db, celery
from app.models.user import User, UserProfile
from app.models.job import Job
from app.models.application import MatchHistory
from app.services.job_matcher import calculate_match_score
from app.services.notification_service import send_new_job_match_notification

@celery.task
def check_matches_for_new_job(job_id):
    """Check all users for matches when a new job is posted"""
    job = Job.query.get(job_id)
    if not job or not job.is_active:
        return
    
    # Get all active job seekers with complete profiles
    users = User.query.filter_by(role='job_seeker', is_active=True).all()
    
    for user in users:
        if not user.profile or not user.profile.skills:
            continue
        
        # Calculate match score
        scores = calculate_match_score(user.profile.to_dict(), job.to_dict())
        
        # If good match (>70%), notify user
        if scores['overall'] >= 70:
            # Save match history
            match_history = MatchHistory(
                user_id=user.id,
                job_id=job.id,
                match_score=scores['overall'],
                skill_match_score=scores['skill_match'],
                experience_match_score=scores['experience_match'],
                location_match_score=scores['location_match']
            )
            db.session.add(match_history)
            
            # Send notification if user has phone number
            if user.profile.phone:
                send_new_job_match_notification.delay(
                    user.profile.phone,
                    user.first_name,
                    job.title,
                    scores['overall']
                )
    
    db.session.commit()

def trigger_job_matching(job):
    """Trigger matching process for a job"""
    check_matches_for_new_job.delay(job.id)
