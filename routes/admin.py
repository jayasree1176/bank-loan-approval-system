from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.database import query_db, execute_db
from utils.helper import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_required
def index():
    users = query_db("SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC")
    logs = query_db("""
        SELECT l.id, u.username, l.action, l.timestamp 
        FROM system_logs l 
        LEFT JOIN users u ON l.user_id = u.id 
        ORDER BY l.timestamp DESC LIMIT 15
    """)
    
    total_users = len(users)
    total_apps = query_db("SELECT COUNT(*) as cnt FROM applications", one=True)['cnt']
    approved_count = query_db("SELECT COUNT(*) as cnt FROM applications WHERE prediction_status = 'Approved'", one=True)['cnt']
    rejected_count = query_db("SELECT COUNT(*) as cnt FROM applications WHERE prediction_status = 'Rejected'", one=True)['cnt']
    
    stats = {
        'total_users': total_users,
        'total_applications': total_apps,
        'approved_count': approved_count,
        'rejected_count': rejected_count
    }
    
    return render_template('admin.html', users=users, logs=logs, stats=stats)

@admin_bp.route('/admin/user/<int:user_id>/toggle-role', methods=['POST'])
@admin_required
def toggle_user_role(user_id):
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.index'))
        
    new_role = 'admin' if user['role'] == 'user' else 'user'
    execute_db("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    execute_db("INSERT INTO system_logs (user_id, action) VALUES (?, ?)", (session['user_id'], f"Changed role for user '{user['username']}' to {new_role}"))
    
    flash(f"User '{user['username']}' role updated to {new_role}.", "success")
    return redirect(url_for('admin.index'))

@admin_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash("Cannot delete your own active admin account.", "danger")
        return redirect(url_for('admin.index'))
        
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if user:
        execute_db("DELETE FROM users WHERE id = ?", (user_id,))
        execute_db("INSERT INTO system_logs (user_id, action) VALUES (?, ?)", (session['user_id'], f"Deleted user account '{user['username']}'"))
        flash(f"User '{user['username']}' deleted.", "success")
        
    return redirect(url_for('admin.index'))
