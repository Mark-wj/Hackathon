from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from celery import Celery  # Add this import
import os
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
celery = Celery()  # Add this line

def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://mark:supersecret@localhost:5432/jobmatch"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Mail Configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Celery Configuration
    app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Initialize Celery
    init_celery(app)
    
    # Import models to ensure they're registered
    from app.models import user, job, application
    
    # Register blueprints AFTER app creation
    register_blueprints(app)
    
    # Register template routes
    register_template_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def init_celery(app):
    """Initialize Celery with Flask app"""
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask

def register_blueprints(app):
    """Register all blueprint routes"""
    
    # Authentication routes
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Dashboard routes - import here to avoid circular import
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    
    # User routes
    from app.routes.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Job routes
    from app.routes.jobs import bp as jobs_bp
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    
    # Application routes
    from app.routes.applications import bp as applications_bp
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    
    # Employer routes
    from app.routes.employer import bp as employer_bp
    app.register_blueprint(employer_bp, url_prefix='/api/employer')
    
    # Admin routes
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # AI services routes (if you have them)
    try:
        from app.routes.ai_services import bp as ai_bp
        app.register_blueprint(ai_bp, url_prefix='/api/ai')
    except ImportError:
        pass  # AI services not implemented yet

def register_template_routes(app):
    """Register template routes for role-based dashboards"""
    
    @app.route('/')
    def index():
        """Job seeker dashboard"""
        return render_template('index.html')
    
    @app.route('/employer')
    def employer():
        """Employer dashboard"""
        return render_template('employer.html')
    
    @app.route('/admin')
    def admin():
        """Admin dashboard"""
        return render_template('admin.html')

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('index.html'), 500