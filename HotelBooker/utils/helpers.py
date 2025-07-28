from datetime import datetime, timedelta
import random
import string
from flask import flash
from app import db
from models import Room, Reservation

def calculate_total_price(room_id, check_in_date, check_out_date):
    """Calculate the total price for a reservation based on room and dates."""
    room = Room.query.get(room_id)
    if not room:
        return 0
    
    # Convert date strings to datetime objects if needed
    if isinstance(check_in_date, str):
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
    if isinstance(check_out_date, str):
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d').date()
    
    # Calculate number of nights
    delta = check_out_date - check_in_date
    num_nights = delta.days
    
    if num_nights <= 0:
        return 0
    
    # Calculate total price
    total_price = room.price_per_night * num_nights
    
    return round(total_price, 2)

def get_available_rooms(check_in_date, check_out_date, num_guests=1, room_type=None):
    """Get available rooms for the given date range and criteria."""
    # Convert date strings to datetime objects if needed
    if isinstance(check_in_date, str):
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
    if isinstance(check_out_date, str):
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d').date()
    
    # Find rooms that are already booked during the period
    booked_room_ids = db.session.query(Reservation.room_id).filter(
        Reservation.status.in_(['confirmed', 'pending', 'checked-in']),
        Reservation.check_out_date > check_in_date,
        Reservation.check_in_date < check_out_date
    ).all()
    
    booked_room_ids = [r[0] for r in booked_room_ids]
    
    # Query for available rooms
    query = Room.query.filter(
        Room.status == 'available',
        Room.capacity >= num_guests,
        ~Room.id.in_(booked_room_ids) if booked_room_ids else True
    )
    
    # Filter by room type if specified
    if room_type:
        query = query.filter(Room.room_type == room_type)
    
    return query.all()

def generate_transaction_id(length=12):
    """Generate a random transaction ID for payments."""
    chars = string.ascii_uppercase + string.digits
    return 'TXN_' + ''.join(random.choice(chars) for _ in range(length))

def flash_form_errors(form):
    """Flash all form validation errors."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")
