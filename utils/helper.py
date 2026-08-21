from functools import wraps
from flask import session, redirect, url_for, flash
import datetime

def login_required(f):
    """Decorator to enforce authenticated session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to enforce admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access the admin portal.", "warning")
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash("Access denied: Administrative privileges required.", "danger")
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def format_currency(value):
    """Format numbers to standard USD currency string ($123,456.00)."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def format_date(value_str):
    """Format timestamp ISO strings to human readable dates."""
    if not value_str:
        return "N/A"
    try:
        dt = datetime.datetime.strptime(str(value_str).split('.')[0], '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%b %d, %Y %I:%M %p')
    except Exception:
        return str(value_str)
