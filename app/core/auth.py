"""
Authentication utilities
"""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from app import login_manager
from app.models.user import User


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function


def engineer_required(f):
    """Decorator to require engineer or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role not in ['engineer', 'admin']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function


def create_default_users():
    """Create default users for demo"""
    from app import db
    
    users = [
        {
            'username': 'demo',
            'email': 'demo@demo.com',
            'password': 'demo',
            'role': 'admin'
        },
        {
            'username': 'engineer',
            'email': 'engineer@demo.com',
            'password': 'engineer123',
            'role': 'engineer'
        },
        {
            'username': 'operator',
            'email': 'operator@demo.com',
            'password': 'operator123',
            'role': 'operator'
        }
    ]
    
    for user_data in users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
    
    db.session.commit()
    print('Default users created!')