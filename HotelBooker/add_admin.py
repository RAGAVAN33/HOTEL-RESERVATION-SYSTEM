import sys
import os
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user(name, email, password, phone=None):
    """
    Create a new admin user.
    
    Args:
        name (str): Admin name
        email (str): Admin email
        password (str): Admin password
        phone (str, optional): Admin phone number
    
    Returns:
        User: The created admin user
    """
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            return existing_user
        
        # Create new admin user
        admin = User(
            name=name,
            email=email,
            phone=phone,
            is_admin=True
        )
        admin.set_password(password)
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user created successfully: {email}")
        return admin

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python add_admin.py <name> <email> <password> [phone]")
        sys.exit(1)
    
    name = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    phone = sys.argv[4] if len(sys.argv) > 4 else None
    
    create_admin_user(name, email, password, phone)