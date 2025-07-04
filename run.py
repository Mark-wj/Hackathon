import os
from app import create_app, db
from app.models import user, job, application

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in flask shell"""
    return {
        'db': db,
        'User': user.User,
        'UserProfile': user.UserProfile,
        'Company': job.Company,
        'Job': job.Job,
        'Application': application.Application,
        'MatchHistory': application.MatchHistory
    }

if __name__ == '__main__':
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
