from datetime import datetime, timedelta, date

def str_to_date(date_str, format_str='%Y-%m-%d'):
    """Convert string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, format_str).date()
    except ValueError:
        return None

def date_to_str(date_obj, format_str='%Y-%m-%d'):
    """Convert date object to string."""
    if not date_obj:
        return ""
    try:
        return date_obj.strftime(format_str)
    except (ValueError, AttributeError):
        return ""

def calculate_nights(check_in_date, check_out_date):
    """Calculate the number of nights between check-in and check-out."""
    if isinstance(check_in_date, str):
        check_in_date = str_to_date(check_in_date)
    if isinstance(check_out_date, str):
        check_out_date = str_to_date(check_out_date)
    
    if not check_in_date or not check_out_date:
        return 0
    
    delta = check_out_date - check_in_date
    return delta.days

def get_date_range(start_date, end_date):
    """Get a list of dates between start_date and end_date (inclusive)."""
    if isinstance(start_date, str):
        start_date = str_to_date(start_date)
    if isinstance(end_date, str):
        end_date = str_to_date(end_date)
    
    if not start_date or not end_date or start_date > end_date:
        return []
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates

def get_today():
    """Get today's date."""
    return date.today()

def get_tomorrow():
    """Get tomorrow's date."""
    return date.today() + timedelta(days=1)

def get_month_start_end(year, month):
    """Get the start and end dates for a specific month."""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    return start_date, end_date

def date_range_overlap(start1, end1, start2, end2):
    """Check if two date ranges overlap."""
    return max(start1, start2) <= min(end1, end2)
