"""Seed database with initial data"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.core.seeder import seed_all_demos

def seed_database():
    """Seed database with initial data"""
    app = create_app()
    
    with app.app_context():
        print("Seeding database...")
        seed_all_demos()
        print("✅ Database seeded successfully!")

if __name__ == '__main__':
    seed_database()