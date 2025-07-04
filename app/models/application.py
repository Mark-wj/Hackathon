from datetime import datetime
from app import db

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    match_score = db.Column(db.Float)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job': self.job.to_dict() if self.job else None,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'match_score': self.match_score,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MatchHistory(db.Model):
    __tablename__ = 'match_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    match_score = db.Column(db.Float)
    skill_match_score = db.Column(db.Float)
    experience_match_score = db.Column(db.Float)
    location_match_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='matches')
    
    def to_dict(self):
        return {
            'id': self.id,
            'job': self.job.to_dict() if self.job else None,
            'match_score': self.match_score,
            'skill_match_score': self.skill_match_score,
            'experience_match_score': self.experience_match_score,
            'location_match_score': self.location_match_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
