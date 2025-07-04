from datetime import datetime
from app import db

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    location = db.Column(db.String(255))
    website = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='company', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'industry': self.industry,
            'size': self.size,
            'location': self.location,
            'website': self.website
        }

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    skills_required = db.Column(db.ARRAY(db.String))
    experience_level = db.Column(db.String(50))
    job_type = db.Column(db.String(50))
    location = db.Column(db.String(255))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    is_remote = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic')
    matches = db.relationship('MatchHistory', backref='job', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company.to_dict() if self.company else None,
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'skills_required': self.skills_required,
            'experience_level': self.experience_level,
            'job_type': self.job_type,
            'location': self.location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'is_remote': self.is_remote,
            'is_active': self.is_active,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
