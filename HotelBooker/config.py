import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-key-for-hotel-reservation')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hotel_reservation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Room types and their capacity
    ROOM_TYPES = {
        'Single': {'capacity': 1, 'base_price': 80.0},
        'Double': {'capacity': 2, 'base_price': 120.0},
        'Deluxe': {'capacity': 2, 'base_price': 180.0},
        'Family': {'capacity': 4, 'base_price': 220.0},
        'Suite': {'capacity': 3, 'base_price': 250.0},
        'Presidential Suite': {'capacity': 5, 'base_price': 400.0}
    }
    
    # Reservation statuses
    RESERVATION_STATUSES = [
        'pending',
        'confirmed', 
        'checked-in', 
        'checked-out', 
        'cancelled'
    ]
    
    # Room statuses
    ROOM_STATUSES = [
        'available',
        'occupied',
        'maintenance',
        'cleaning'
    ]
    
    # Payment methods
    PAYMENT_METHODS = [
        'credit_card',
        'debit_card',
        'cash',
        'bank_transfer'
    ]
    
    # Payment statuses
    PAYMENT_STATUSES = [
        'pending',
        'completed',
        'failed',
        'refunded'
    ]
    
    # Default admin credentials
    DEFAULT_ADMIN_NAME = 'Admin'
    DEFAULT_ADMIN_EMAIL = 'admin@hotel.com'
    DEFAULT_ADMIN_PASSWORD = 'admin123'  # Should be changed in production
