"""
User model for authentication
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app.core.database import BaseModel, TimestampMixin


class User(UserMixin, BaseModel, TimestampMixin):
    """User model"""
    __tablename__ = 'users'
    
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='operator', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Roles: admin, engineer, operator, viewer
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        """Convert to dictionary (excluding password)"""
        data = super().to_dict()
        data.pop('password_hash', None)
        return data