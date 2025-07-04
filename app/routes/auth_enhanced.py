from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserProfile
from app.utils.validators import validate_email, validate_password
from app.services.email_service import send_verification_email
import secrets

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user with email verification"""
    data = request.get_json()
    
    # Validate input
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'job_seeker')
    
    if role not in ['job_seeker', 'employer']:
        return jsonify({'error': 'Invalid role. Must be job_seeker or employer'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not validate_password(password):
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    user = User(
        email=email,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role=role,
        is_active=False  # Inactive until email verified
    )
    user.set_password(password)
    
    # Generate verification token
    user.email_verification_token = secrets.token_urlsafe(32)
    
    # Create user profile
    profile = UserProfile(user=user)
    
    db.session.add(user)
    db.session.add(profile)
    db.session.commit()
    
    # Send verification email
    send_verification_email(user.email, user.email_verification_token)
    
    return jsonify({
        'message': 'Registration successful! Please check your email to verify your account.',
        'role': user.role
    }), 201

@bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify email address"""
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid verification token'}), 400
    
    user.is_active = True
    user.email_verified = True
    user.email_verification_token = None
    db.session.commit()
    
    return jsonify({'message': 'Email verified successfully! You can now login.'}), 200

@bp.route('/login', methods=['POST'])
def login():
    """Login user with role-based response"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Please verify your email first'}), 403
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Include redirect URL based on role
    redirect_urls = {
        'job_seeker': '/',
        'employer': '/employer',
        'admin': '/admin'
    }
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
        'redirect_url': redirect_urls.get(user.role, '/')
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({'access_token': access_token}), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens)"""
    return jsonify({'message': 'Successfully logged out'}), 200

@bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.email_verified:
        return jsonify({'message': 'Email already verified'}), 200
    
    # Generate new token
    user.email_verification_token = secrets.token_urlsafe(32)
    db.session.commit()
    
    # Send verification email
    send_verification_email(user.email, user.email_verification_token)
    
    return jsonify({'message': 'Verification email sent'}), 200
