"""Reset database (WARNING: Deletes all data)"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

def reset_database():
    """Reset database - DROP ALL TABLES"""
    app = create_app()
    
    response = input("⚠️  WARNING: This will delete ALL data. Are you sure? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Reset cancelled.")
        return
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating fresh tables...")
        db.create_all()
        print("✅ Database reset complete!")

if __name__ == '__main__':
    reset_database()