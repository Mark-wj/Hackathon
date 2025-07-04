from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
celery = Celery()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Register blueprints
    from app.routes import auth, users, jobs, applications, ai_services
    from app.routes import employer, admin
    from app.routes import frontend
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(jobs.bp, url_prefix='/api/jobs')
    app.register_blueprint(applications.bp, url_prefix='/api/applications')
    app.register_blueprint(ai_services.bp, url_prefix='/api/ai')
    app.register_blueprint(frontend.bp)
    app.register_blueprint(employer.bp, url_prefix="/api/employer")
    app.register_blueprint(admin.bp, url_prefix="/api/admin")
    
    return app