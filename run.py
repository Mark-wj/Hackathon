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

if __name__ == "__main__":
    # create all tables defined by your SQLAlchemy models
    with app.app_context():
        print("→ SQLALCHEMY_DATABASE_URI:", app.config["SQLALCHEMY_DATABASE_URI"])
        db.create_all()

    # then start the server
    app.run(debug=True, host="0.0.0.0")