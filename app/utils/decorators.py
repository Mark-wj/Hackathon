from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.user import User
from app import celery

def admin_required():
    """Decorator to require admin role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def employer_required():
    """Decorator to require employer role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role not in ['employer', 'admin']:
                return jsonify({'error': 'Employer access required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def async_task(f):
    """Decorator to run function as async task"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        task = celery.task(f)
        return task.delay(*args, **kwargs)
    return decorated_function
