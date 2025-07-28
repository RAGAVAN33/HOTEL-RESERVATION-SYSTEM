from app import app, db
from models import User
from werkzeug.security import generate_password_hash
import getpass
import re

def is_valid_email(email):
    """Check if the email is valid."""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))

def create_admin_user_interactive():
    """
    Interactively create a new admin user by prompting for details.
    """
    print("\n=== Create New Admin User ===\n")
    
    # Get admin details with validation
    while True:
        name = input("Enter admin name: ").strip()
        if name:
            break
        print("Name cannot be empty.")
    
    while True:
        email = input("Enter admin email: ").strip()
        if not email:
            print("Email cannot be empty.")
            continue
        if not is_valid_email(email):
            print("Please enter a valid email address.")
            continue
            
        # Check if email already exists
        with app.app_context():
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"A user with email {email} already exists.")
                choice = input("Do you want to update this user to admin? (y/n): ").lower()
                if choice == 'y':
                    existing_user.is_admin = True
                    db.session.commit()
                    print(f"User {email} has been updated to admin.")
                    return
                else:
                    continue
        break
    
    while True:
        password = getpass.getpass("Enter admin password: ")
        if len(password) < 6:
            print("Password must be at least 6 characters long.")
            continue
            
        confirm_password = getpass.getpass("Confirm admin password: ")
        if password != confirm_password:
            print("Passwords do not match.")
            continue
        break
    
    phone = input("Enter admin phone (optional): ").strip()
    
    # Create admin user
    with app.app_context():
        admin = User(
            name=name,
            email=email,
            phone=phone if phone else None,
            is_admin=True
        )
        admin.set_password(password)
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        print(f"\nAdmin user created successfully: {email}")

if __name__ == "__main__":
    create_admin_user_interactive()