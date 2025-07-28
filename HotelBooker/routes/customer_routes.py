from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app import db
from models import Room, Reservation, Payment, User
from utils.helpers import calculate_total_price, get_available_rooms, generate_transaction_id
from utils.date_utils import str_to_date, calculate_nights, get_today, get_tomorrow
from datetime import datetime, timedelta

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def index():
    """Home page with search form."""
    return render_template('index.html')

@customer_bp.route('/rooms/search', methods=['GET', 'POST'])
def room_search():
    """Search for available rooms based on criteria."""
    if request.method == 'POST':
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        guests = int(request.form.get('guests', 1))
        room_type = request.form.get('room_type', '')
        
        # Store search parameters in session
        session['search'] = {
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
            'room_type': room_type
        }
        
        return redirect(url_for('customer.room_search'))
    
    # Handle GET request or redirected POST
    search = session.get('search', {
        'check_in': get_today().strftime('%Y-%m-%d'),
        'check_out': get_tomorrow().strftime('%Y-%m-%d'),
        'guests': 1,
        'room_type': ''
    })
    
    check_in_date = str_to_date(search.get('check_in'))
    check_out_date = str_to_date(search.get('check_out'))
    num_guests = int(search.get('guests', 1))
    room_type = search.get('room_type', '')
    
    if not check_in_date or not check_out_date:
        flash('Please select valid dates', 'warning')
        return redirect(url_for('customer.index'))
    
    if check_in_date >= check_out_date:
        flash('Check-out date must be after check-in date', 'warning')
        return redirect(url_for('customer.index'))
    
    if check_in_date < get_today():
        flash('Check-in date cannot be in the past', 'warning')
        return redirect(url_for('customer.index'))
    
    # Get available rooms
    available_rooms = get_available_rooms(check_in_date, check_out_date, num_guests, room_type if room_type else None)
    
    # Get all unique room types for filter
    room_types = db.session.query(Room.room_type).distinct().all()
    room_types = [r[0] for r in room_types]
    
    nights = calculate_nights(check_in_date, check_out_date)
    
    return render_template('customer/room_search.html', 
                          rooms=available_rooms,
                          room_types=room_types,
                          search=search,
                          nights=nights)

@customer_bp.route('/rooms/<int:room_id>')
def room_detail(room_id):
    """Show details for a specific room."""
    room = Room.query.get_or_404(room_id)
    
    # Get search parameters from session
    search = session.get('search', {
        'check_in': get_today().strftime('%Y-%m-%d'),
        'check_out': get_tomorrow().strftime('%Y-%m-%d'),
        'guests': 1
    })
    
    check_in_date = str_to_date(search.get('check_in'))
    check_out_date = str_to_date(search.get('check_out'))
    nights = calculate_nights(check_in_date, check_out_date)
    total_price = calculate_total_price(room_id, check_in_date, check_out_date)
    
    return render_template('customer/room_detail.html', 
                          room=room,
                          check_in=search.get('check_in'),
                          check_out=search.get('check_out'),
                          guests=search.get('guests'),
                          nights=nights,
                          total_price=total_price)

@customer_bp.route('/booking/<int:room_id>', methods=['GET', 'POST'])
@login_required
def booking(room_id):
    """Book a room."""
    room = Room.query.get_or_404(room_id)
    
    # Get search parameters from session
    search = session.get('search', {
        'check_in': get_today().strftime('%Y-%m-%d'),
        'check_out': get_tomorrow().strftime('%Y-%m-%d'),
        'guests': 1
    })
    
    check_in_date = str_to_date(search.get('check_in'))
    check_out_date = str_to_date(search.get('check_out'))
    guests = int(search.get('guests', 1))
    nights = calculate_nights(check_in_date, check_out_date)
    total_price = calculate_total_price(room_id, check_in_date, check_out_date)
    
    if request.method == 'POST':
        # Validate dates and availability again
        if check_in_date >= check_out_date:
            flash('Check-out date must be after check-in date', 'danger')
            return redirect(url_for('customer.room_detail', room_id=room_id))
        
        if check_in_date < get_today():
            flash('Check-in date cannot be in the past', 'danger')
            return redirect(url_for('customer.room_detail', room_id=room_id))
        
        # Check if room is still available
        available_rooms = get_available_rooms(check_in_date, check_out_date, guests)
        if room not in available_rooms:
            flash('Sorry, this room is no longer available for the selected dates', 'danger')
            return redirect(url_for('customer.room_search'))
        
        # Create reservation
        reservation = Reservation(
            user_id=current_user.id,
            room_id=room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            num_guests=guests,
            total_price=total_price,
            status='pending'
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        # Create payment record (simulated)
        payment_method = request.form.get('payment_method', 'credit_card')
        payment = Payment(
            reservation_id=reservation.id,
            amount=total_price,
            payment_method=payment_method,
            transaction_id=generate_transaction_id(),
            status='completed'  # Simulate instant payment completion
        )
        
        db.session.add(payment)
        
        # Update reservation status
        reservation.status = 'confirmed'
        
        db.session.commit()
        
        flash('Your reservation has been confirmed!', 'success')
        return redirect(url_for('customer.my_reservations'))
    
    return render_template('customer/booking.html', 
                          room=room,
                          check_in=search.get('check_in'),
                          check_out=search.get('check_out'),
                          guests=guests,
                          nights=nights,
                          total_price=total_price)

@customer_bp.route('/my-reservations')
@login_required
def my_reservations():
    """Show user's reservations."""
    # Get all reservations for the current user
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.created_at.desc()).all()
    
    # Get current date for template
    now = datetime.now().date()
    
    return render_template('customer/my_reservations.html', reservations=reservations, now=now, timedelta=timedelta)

@customer_bp.route('/reservation/<int:reservation_id>')
@login_required
def reservation_detail(reservation_id):
    """Show details for a specific reservation."""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Security check - ensure the reservation belongs to the current user
    if reservation.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this reservation', 'danger')
        return redirect(url_for('customer.my_reservations'))
    
    # Get payment information
    payment = Payment.query.filter_by(reservation_id=reservation_id).first()
    
    # Get current date for template
    now = datetime.now().date()
    
    return render_template('customer/reservation_detail.html', 
                          reservation=reservation,
                          payment=payment,
                          now=now,
                          timedelta=timedelta)

@customer_bp.route('/reservation/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    """Cancel a reservation."""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Security check - ensure the reservation belongs to the current user
    if reservation.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to cancel this reservation', 'danger')
        return redirect(url_for('customer.my_reservations'))
    
    # Check if the reservation can be cancelled
    if reservation.status not in ['pending', 'confirmed']:
        flash('This reservation cannot be cancelled', 'danger')
        return redirect(url_for('customer.reservation_detail', reservation_id=reservation_id))
    
    # Check cancellation policy (e.g., cannot cancel if check-in is within 24 hours)
    if reservation.check_in_date <= (get_today() + timedelta(days=1)):
        flash('Reservations cannot be cancelled within 24 hours of check-in', 'danger')
        return redirect(url_for('customer.reservation_detail', reservation_id=reservation_id))
    
    # Update reservation status
    reservation.status = 'cancelled'
    
    # Update payment status to refunded (simulated)
    payment = Payment.query.filter_by(reservation_id=reservation_id).first()
    if payment:
        payment.status = 'refunded'
    
    db.session.commit()
    
    flash('Your reservation has been cancelled successfully', 'success')
    return redirect(url_for('customer.my_reservations'))
