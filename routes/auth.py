from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.database import query_db, execute_db
from utils.helper import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template('login.html')
            
        user = query_db("SELECT * FROM users WHERE username = ? OR email = ?", (username, username), one=True)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            
            # Log login action
            execute_db("INSERT INTO system_logs (user_id, action) VALUES (?, ?)", (user['id'], "User logged in"))
            
            flash(f"Welcome back, {user['username']}!", "success")
            if user['role'] == 'admin':
                return redirect(url_for('admin.index'))
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid username/email or password.", "danger")
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html')
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')
            
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template('register.html')
            
        # Check existing user
        existing = query_db("SELECT * FROM users WHERE username = ? OR email = ?", (username, email), one=True)
        if existing:
            flash("Username or Email already registered. Please login.", "warning")
            return render_template('register.html')
            
        hashed = generate_password_hash(password)
        new_user_id = execute_db(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, 'user')",
            (username, email, hashed)
        )
        
        # Log action
        execute_db("INSERT INTO system_logs (user_id, action) VALUES (?, ?)", (new_user_id, "User registered account"))
        
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        execute_db("INSERT INTO system_logs (user_id, action) VALUES (?, ?)", (user_id, "User logged out"))
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    
    # User's prediction stats
    stats = query_db("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN prediction_status = 'Approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN prediction_status = 'Rejected' THEN 1 ELSE 0 END) as rejected
        FROM applications WHERE user_id = ?
    """, (user_id,), one=True)
    
    if request.method == 'POST':
        new_email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '').strip()
        
        if new_email:
            execute_db("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
            session['email'] = new_email
            
        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
            else:
                hashed = generate_password_hash(new_password)
                execute_db("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
                flash("Password updated successfully.", "success")
                
        flash("Profile updated successfully.", "success")
        return redirect(url_for('auth.profile'))
        
    return render_template('profile.html', user=user, stats=stats)
