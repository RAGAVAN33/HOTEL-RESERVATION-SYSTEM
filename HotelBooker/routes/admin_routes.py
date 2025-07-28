from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app import db
from models import Room, Reservation, Payment, User
from utils.auth import admin_required
from utils.helpers import calculate_total_price
from utils.date_utils import str_to_date, get_today, get_tomorrow, get_month_start_end
from datetime import datetime, timedelta
from sqlalchemy import func
import calendar
import re

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with key metrics."""
    # Count today's check-ins and check-outs
    today = get_today()
    checkins_today = Reservation.query.filter_by(check_in_date=today).count()
    checkouts_today = Reservation.query.filter_by(check_out_date=today).count()
    
    # Count current occupied rooms
    occupied_rooms = Reservation.query.filter(
        Reservation.status.in_(['confirmed', 'checked-in']),
        Reservation.check_in_date <= today,
        Reservation.check_out_date > today
    ).count()
    
    # Count total rooms
    total_rooms = Room.query.count()
    
    # Calculate occupancy rate
    occupancy_rate = round((occupied_rooms / total_rooms * 100), 2) if total_rooms > 0 else 0
    
    # Get revenue for current month
    current_month = today.month
    current_year = today.year
    start_date, end_date = get_month_start_end(current_year, current_month)
    
    monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).scalar()
    
    monthly_revenue = monthly_revenue or 0
    
    # Get upcoming reservations (next 7 days)
    upcoming_reservations = Reservation.query.filter(
        Reservation.check_in_date > today,
        Reservation.check_in_date <= today + timedelta(days=7),
        Reservation.status == 'confirmed'
    ).order_by(Reservation.check_in_date).all()
    
    # Count total active reservations
    active_reservations = Reservation.query.filter(
        Reservation.status.in_(['confirmed', 'checked-in'])
    ).count()
    
    return render_template('admin/dashboard.html',
                          checkins_today=checkins_today,
                          checkouts_today=checkouts_today,
                          occupied_rooms=occupied_rooms,
                          total_rooms=total_rooms,
                          occupancy_rate=occupancy_rate,
                          monthly_revenue=monthly_revenue,
                          upcoming_reservations=upcoming_reservations,
                          active_reservations=active_reservations)

@admin_bp.route('/rooms')
@login_required
@admin_required
def room_management():
    """Manage rooms (view, add, edit, delete)."""
    rooms = Room.query.all()
    return render_template('admin/room_management.html', rooms=rooms)

@admin_bp.route('/rooms/add', methods=['POST'])
@login_required
@admin_required
def add_room():
    """Add a new room."""
    room_number = request.form.get('room_number')
    room_type = request.form.get('room_type')
    price = float(request.form.get('price', 0))
    capacity = int(request.form.get('capacity', 1))
    description = request.form.get('description', '')
    status = request.form.get('status', 'available')
    
    # Check if room number already exists
    existing_room = Room.query.filter_by(room_number=room_number).first()
    if existing_room:
        flash('A room with this number already exists', 'danger')
        return redirect(url_for('admin.room_management'))
    
    # Create new room
    room = Room(
        room_number=room_number,
        room_type=room_type,
        price_per_night=price,
        capacity=capacity,
        description=description,
        status=status
    )
    
    db.session.add(room)
    db.session.commit()
    
    flash('Room added successfully', 'success')
    return redirect(url_for('admin.room_management'))

@admin_bp.route('/rooms/edit/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def edit_room(room_id):
    """Edit an existing room."""
    room = Room.query.get_or_404(room_id)
    
    room.room_number = request.form.get('room_number')
    room.room_type = request.form.get('room_type')
    room.price_per_night = float(request.form.get('price', 0))
    room.capacity = int(request.form.get('capacity', 1))
    room.description = request.form.get('description', '')
    room.status = request.form.get('status', 'available')
    
    db.session.commit()
    
    flash('Room updated successfully', 'success')
    return redirect(url_for('admin.room_management'))

@admin_bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    """Delete a room."""
    room = Room.query.get_or_404(room_id)
    
    # Check if room has active reservations
    active_reservations = Reservation.query.filter(
        Reservation.room_id == room_id,
        Reservation.status.in_(['confirmed', 'checked-in'])
    ).first()
    
    if active_reservations:
        flash('Cannot delete room with active reservations', 'danger')
        return redirect(url_for('admin.room_management'))
    
    db.session.delete(room)
    db.session.commit()
    
    flash('Room deleted successfully', 'success')
    return redirect(url_for('admin.room_management'))

@admin_bp.route('/reservations')
@login_required
@admin_required
def reservation_management():
    """Manage all reservations."""
    status_filter = request.args.get('status', 'all')
    
    # Build query based on filter
    query = Reservation.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Sort by check-in date (default)
    sort_by = request.args.get('sort', 'check_in')
    
    if sort_by == 'check_in':
        query = query.order_by(Reservation.check_in_date)
    elif sort_by == 'created':
        query = query.order_by(Reservation.created_at.desc())
    elif sort_by == 'status':
        query = query.order_by(Reservation.status)
    
    reservations = query.all()
    
    # Get current date for template
    now = datetime.now().date()
    
    return render_template('admin/reservation_management.html', 
                          reservations=reservations, 
                          status_filter=status_filter,
                          sort_by=sort_by,
                          now=now,
                          timedelta=timedelta)

@admin_bp.route('/reservation/<int:reservation_id>')
@login_required
@admin_required
def reservation_detail(reservation_id):
    """View details of a specific reservation."""
    reservation = Reservation.query.get_or_404(reservation_id)
    payment = Payment.query.filter_by(reservation_id=reservation_id).first()
    
    # Get current date for template
    now = datetime.now().date()
    
    return render_template('admin/reservation_detail.html', 
                          reservation=reservation,
                          payment=payment,
                          now=now,
                          timedelta=timedelta)

@admin_bp.route('/reservation/<int:reservation_id>/update', methods=['POST'])
@login_required
@admin_required
def update_reservation_status(reservation_id):
    """Update reservation status."""
    reservation = Reservation.query.get_or_404(reservation_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'confirmed', 'checked-in', 'checked-out', 'cancelled']:
        reservation.status = new_status
        db.session.commit()
        flash(f'Reservation status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'danger')
    
    return redirect(url_for('admin.reservation_detail', reservation_id=reservation_id))

@admin_bp.route('/checkin-checkout')
@login_required
@admin_required
def checkin_checkout():
    """Manage check-ins and check-outs for today."""
    today = get_today()
    
    # Get today's check-ins
    checkins = Reservation.query.filter(
        Reservation.check_in_date == today,
        Reservation.status.in_(['confirmed'])
    ).all()
    
    # Get today's check-outs
    checkouts = Reservation.query.filter(
        Reservation.check_out_date == today,
        Reservation.status.in_(['checked-in'])
    ).all()
    
    return render_template('admin/checkin_checkout.html',
                          checkins=checkins,
                          checkouts=checkouts,
                          today=today,
                          timedelta=timedelta)

@admin_bp.route('/checkin/<int:reservation_id>', methods=['POST'])
@login_required
@admin_required
def checkin(reservation_id):
    """Process check-in for a reservation."""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.status != 'confirmed':
        flash('Only confirmed reservations can be checked in', 'danger')
        return redirect(url_for('admin.checkin_checkout'))
    
    # Update reservation status
    reservation.status = 'checked-in'
    
    # Update room status
    room = Room.query.get(reservation.room_id)
    room.status = 'occupied'
    
    db.session.commit()
    
    flash(f'Check-in processed for reservation #{reservation_id}', 'success')
    return redirect(url_for('admin.checkin_checkout'))

@admin_bp.route('/checkout/<int:reservation_id>', methods=['POST'])
@login_required
@admin_required
def checkout(reservation_id):
    """Process check-out for a reservation."""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.status != 'checked-in':
        flash('Only checked-in reservations can be checked out', 'danger')
        return redirect(url_for('admin.checkin_checkout'))
    
    # Update reservation status
    reservation.status = 'checked-out'
    
    # Update room status to cleaning (then will need to be set to available later)
    room = Room.query.get(reservation.room_id)
    room.status = 'cleaning'
    
    db.session.commit()
    
    flash(f'Check-out processed for reservation #{reservation_id}', 'success')
    return redirect(url_for('admin.checkin_checkout'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Generate and display reports."""
    report_type = request.args.get('type', 'occupancy')
    
    # Get current month and year
    today = get_today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    
    # Get start and end dates for selected month
    start_date, end_date = get_month_start_end(year, month)
    
    # Month name for display
    month_name = calendar.month_name[month]
    
    if report_type == 'occupancy':
        # Calculate occupancy for each day in the month
        occupancy_data = []
        
        # Get total rooms
        total_rooms = Room.query.count()
        
        current_date = start_date
        while current_date <= end_date:
            # Count occupied rooms on this date
            occupied_rooms = Reservation.query.filter(
                Reservation.status.in_(['confirmed', 'checked-in']),
                Reservation.check_in_date <= current_date,
                Reservation.check_out_date > current_date
            ).count()
            
            # Calculate occupancy rate
            occupancy_rate = round((occupied_rooms / total_rooms * 100), 2) if total_rooms > 0 else 0
            
            occupancy_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day': current_date.day,
                'occupied': occupied_rooms,
                'total': total_rooms,
                'rate': occupancy_rate
            })
            
            current_date += timedelta(days=1)
        
        return render_template('admin/reports.html',
                              report_type=report_type,
                              month=month,
                              year=year,
                              month_name=month_name,
                              data=occupancy_data,
                              timedelta=timedelta)
    
    elif report_type == 'revenue':
        # Calculate revenue for the month
        revenue_data = []
        
        # Get total revenue for the month
        total_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).scalar() or 0
        
        # Get revenue by room type
        revenue_by_type = db.session.query(
            Room.room_type,
            func.sum(Reservation.total_price)
        ).join(Reservation, Room.id == Reservation.room_id)\
        .join(Payment, Reservation.id == Payment.reservation_id)\
        .filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).group_by(Room.room_type).all()
        
        # Get revenue per day
        daily_revenue = db.session.query(
            func.date(Payment.payment_date),
            func.sum(Payment.amount)
        ).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).group_by(func.date(Payment.payment_date)).all()
        
        return render_template('admin/reports.html',
                              report_type=report_type,
                              month=month,
                              year=year,
                              month_name=month_name,
                              total_revenue=total_revenue,
                              revenue_by_type=revenue_by_type,
                              daily_revenue=daily_revenue,
                              timedelta=timedelta)
    
    elif report_type == 'bookings':
        # Get booking statistics for the month
        bookings_data = {}
        
        # Total bookings in the month
        total_bookings = Reservation.query.filter(
            Reservation.created_at >= start_date,
            Reservation.created_at <= end_date
        ).count()
        
        # Bookings by status
        bookings_by_status = db.session.query(
            Reservation.status,
            func.count(Reservation.id)
        ).filter(
            Reservation.created_at >= start_date,
            Reservation.created_at <= end_date
        ).group_by(Reservation.status).all()
        
        # Bookings by room type
        bookings_by_type = db.session.query(
            Room.room_type,
            func.count(Reservation.id)
        ).join(Reservation, Room.id == Reservation.room_id)\
        .filter(
            Reservation.created_at >= start_date,
            Reservation.created_at <= end_date
        ).group_by(Room.room_type).all()
        
        # Average stay duration
        avg_duration = db.session.query(
            func.avg(func.julianday(Reservation.check_out_date) - func.julianday(Reservation.check_in_date))
        ).filter(
            Reservation.created_at >= start_date,
            Reservation.created_at <= end_date
        ).scalar() or 0
        
        bookings_data = {
            'total': total_bookings,
            'by_status': bookings_by_status,
            'by_type': bookings_by_type,
            'avg_duration': round(avg_duration, 1)
        }
        
        return render_template('admin/reports.html',
                              report_type=report_type,
                              month=month,
                              year=year,
                              month_name=month_name,
                              bookings_data=bookings_data,
                              timedelta=timedelta)
    
    # Default to occupancy report
    return redirect(url_for('admin.reports', type='occupancy'))

@admin_bp.route('/users')
@login_required
@admin_required
def user_management():
    """Manage users (view, edit, delete)."""
    users = User.query.all()
    return render_template('admin/user_management.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user or admin."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_admin = 'is_admin' in request.form
        
        # Validate form data
        if not name or not email or not password:
            flash('Name, email, and password are required fields.', 'danger')
            return redirect(url_for('admin.add_user'))
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('admin.add_user'))
            
        # Validate email format
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('admin.add_user'))
            
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash(f'A user with email {email} already exists.', 'danger')
            return redirect(url_for('admin.add_user'))
            
        # Create new user
        user = User(
            name=name,
            email=email,
            phone=phone if phone else None,
            is_admin=is_admin
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'{"Admin" if is_admin else "User"} {email} created successfully.', 'success')
        return redirect(url_for('admin.user_management'))
        
    return render_template('admin/add_user.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit an existing user."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.is_admin = 'is_admin' in request.form
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            confirm_password = request.form.get('confirm_password')
            
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
                
            user.set_password(new_password)
        
        db.session.commit()
        
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.user_management'))
        
    return render_template('admin/edit_user.html', user=user)
