# app/routes/auth_enhanced.py

from flask import Blueprint, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserProfile
from app.utils.validators import validate_email, validate_password
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with role-based response"""
    data = request.get_json()
    
    # Validate input
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'job_seeker')
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not validate_password(password):
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    # Validate role
    if role not in ['job_seeker', 'employer', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    user = User(
        email=email,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role=role
    )
    user.set_password(password)
    
    # Create user profile
    profile = UserProfile(user=user)
    
    db.session.add(user)
    db.session.add(profile)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Determine redirect URL based on role
    redirect_url = get_dashboard_url(user.role)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
        'redirect_url': redirect_url,
        'message': f'Welcome! You have been registered as a {role.replace("_", " ").title()}.'
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with role-based redirect"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account deactivated. Please contact support.'}), 403
    
    # Update last login
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Determine redirect URL based on role
    redirect_url = get_dashboard_url(user.role)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
        'redirect_url': redirect_url,
        'message': f'Welcome back, {user.first_name or user.email}!'
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'Invalid user'}), 401
    
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    # In a production system, you might want to blacklist the token
    return jsonify({'message': 'Successfully logged out'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict(),
        'dashboard_url': get_dashboard_url(user.role)
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password required'}), 400
    
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    if not validate_password(new_password):
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    
    user.set_password(new_password)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Password updated successfully'}), 200

@auth_bp.route('/role-switch', methods=['POST'])
@jwt_required()
def switch_role():
    """Switch user role (for testing purposes or admin actions)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['job_seeker', 'employer', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Only admins can switch to admin role
    if new_role == 'admin' and user.role != 'admin':
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Only allow certain role transitions
    allowed_transitions = {
        'job_seeker': ['employer'],
        'employer': ['job_seeker'],
        'admin': ['job_seeker', 'employer', 'admin']
    }
    
    if new_role not in allowed_transitions.get(user.role, []):
        return jsonify({'error': 'Role transition not allowed'}), 400
    
    user.role = new_role
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': f'Role switched to {new_role.replace("_", " ").title()}',
        'user': user.to_dict(),
        'redirect_url': get_dashboard_url(new_role)
    }), 200

def get_dashboard_url(role):
    """Get dashboard URL based on user role"""
    role_urls = {
        'job_seeker': '/job-seeker',
        'employer': '/employer',
        'admin': '/admin'
    }
    return role_urls.get(role, '/')

# Utility functions for user management

@auth_bp.route('/users/stats', methods=['GET'])
@jwt_required()
def user_stats():
    """Get user statistics (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    job_seekers = User.query.filter_by(role='job_seeker').count()
    employers = User.query.filter_by(role='employer').count()
    admins = User.query.filter_by(role='admin').count()
    
    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_registrations = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': total_users - active_users,
        'roles': {
            'job_seekers': job_seekers,
            'employers': employers,
            'admins': admins
        },
        'recent_registrations': recent_registrations
    }), 200

@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    """Toggle user active status (admin only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Don't allow deactivating other admins
    if target_user.role == 'admin' and target_user.id != current_user.id:
        return jsonify({'error': 'Cannot deactivate other admin accounts'}), 400
    
    target_user.is_active = not target_user.is_active
    target_user.updated_at = datetime.utcnow()
    db.session.commit()
    
    status = 'activated' if target_user.is_active else 'deactivated'
    return jsonify({
        'message': f'User {status} successfully',
        'user': target_user.to_dict()
    }), 200

# Password reset functionality (basic implementation)
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Initiate password reset process"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    # Always return success to prevent email enumeration
    if user:
        # In a real implementation, you would:
        # 1. Generate a secure reset token
        # 2. Store it in the database with expiration
        # 3. Send email with reset link
        pass
    
    return jsonify({
        'message': 'If the email exists, you will receive password reset instructions'
    }), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password required'}), 400
    
    if not validate_password(new_password):
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    # In a real implementation, you would:
    # 1. Validate the reset token
    # 2. Check if it's not expired
    # 3. Update the user's password
    # 4. Invalidate the token
    
    return jsonify({'message': 'Password reset successfully'}), 200