from datetime import datetime
from app import db
from bcrypt import hashpw, gensalt, checkpw

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(50), default='job_seeker')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='user', lazy='dynamic')
    posted_jobs = db.relationship('Job', backref='poster', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(255))
    summary = db.Column(db.Text)
    skills = db.Column(db.ARRAY(db.String))
    experience_years = db.Column(db.Integer)
    education = db.Column(db.JSON)
    work_experience = db.Column(db.JSON)
    resume_file_path = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'phone': self.phone,
            'location': self.location,
            'summary': self.summary,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'education': self.education,
            'work_experience': self.work_experience,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url
        }
