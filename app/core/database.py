"""
Database utilities and base models
"""
from datetime import datetime
from app import db


class TimestampMixin:
    """Mixin to add timestamp fields to models"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class BaseModel(db.Model):
    """Base model with common fields"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    def save(self):
        """Save instance to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete instance from database"""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Update instance fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


def init_db(app):
    """Initialize database"""
    with app.app_context():
        db.create_all()
        print('Database tables created!')


def seed_db(app):
    """Seed database with initial data"""
    with app.app_context():
        from app.core.seeder import seed_all_demos
        seed_all_demos()
        print('Database seeded!')


def reset_db(app):
    """Reset database (WARNING: Deletes all data)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('Database reset complete!')