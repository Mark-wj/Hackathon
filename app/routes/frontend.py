from flask import Blueprint, render_template

bp = Blueprint('frontend', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/employer')
def employer():
    return render_template('employer.html')

@bp.route('/admin')
def admin():
    return render_template('admin.html')

@bp.route('/verify-email/<token>')
def verify_email_page(token):
    return render_template('verify_email.html')
