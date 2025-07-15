import os
from app import create_app, db
from flask_cors import CORS
from app.models import user, job, application

app = create_app()
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5000",
            "http://127.0.0.1:5000",
            "http://192.168.100.10:5000",  # Your network IP
            "http://192.168.100.*:5000"    # Allow any IP in your network range
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
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