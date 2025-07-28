from functools import wraps
from flask import redirect, url_for, flash, session
from flask_login import current_user
from app import db
from models import User
from werkzeug.security import generate_password_hash
from config import Config

def admin_required(f):
    """Decorator for routes that require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def create_default_admin():
    """Create a default admin user if no admin exists."""
    admin = User.query.filter_by(email=Config.DEFAULT_ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            name=Config.DEFAULT_ADMIN_NAME,
            email=Config.DEFAULT_ADMIN_EMAIL,
            is_admin=True
        )
        admin.set_password(Config.DEFAULT_ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"Default admin user created: {Config.DEFAULT_ADMIN_EMAIL}")
    return admin
