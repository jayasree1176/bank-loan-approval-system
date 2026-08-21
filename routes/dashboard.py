from flask import Blueprint, render_template, session, redirect, url_for, flash
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.database import query_db
from utils.helper import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = session['user_id']
    role = session.get('role')
    
    # Query summary metrics
    if role == 'admin':
        total_apps = query_db("SELECT COUNT(*) as cnt FROM applications", one=True)['cnt']
        approved_apps = query_db("SELECT COUNT(*) as cnt FROM applications WHERE prediction_status = 'Approved'", one=True)['cnt']
        rejected_apps = query_db("SELECT COUNT(*) as cnt FROM applications WHERE prediction_status = 'Rejected'", one=True)['cnt']
        high_risk = query_db("SELECT COUNT(*) as cnt FROM applications WHERE risk_level = 'High'", one=True)['cnt']
        medium_risk = query_db("SELECT COUNT(*) as cnt FROM applications WHERE risk_level = 'Medium'", one=True)['cnt']
        low_risk = query_db("SELECT COUNT(*) as cnt FROM applications WHERE risk_level = 'Low'", one=True)['cnt']
        recent_apps = query_db("SELECT * FROM applications ORDER BY created_at DESC LIMIT 6")
    else:
        total_apps = query_db("SELECT COUNT(*) as cnt FROM applications WHERE user_id = ?", (user_id,), one=True)['cnt']
        approved_apps = query_db("SELECT COUNT(*) as cnt FROM applications WHERE user_id = ? AND prediction_status = 'Approved'", (user_id,), one=True)['cnt']
        rejected_apps = query_db("SELECT COUNT(*) as cnt FROM applications WHERE user_id = ? AND prediction_status = 'Rejected'", (user_id,), one=True)['cnt']
        high_risk = query_db("SELECT COUNT(*) as cnt FROM applications WHERE user_id = ? AND risk_level = 'High'", (user_id,), one=True)['cnt']
        medium_risk = query_db("SELECT COUNT(*) as cnt FROM applications WHERE user_id = ? AND risk_level = 'Medium'", (user_id,), one=True)['cnt']
        low_risk = query_db("SELECT COUNT(*) as cnt FROM applications WHERE user_id = ? AND risk_level = 'Low'", (user_id,), one=True)['cnt']
        recent_apps = query_db("SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC LIMIT 6", (user_id,))
        
    approval_rate = round((approved_apps / total_apps * 100), 1) if total_apps > 0 else 0.0
    
    metrics = {
        'total_applications': total_apps,
        'approved_loans': approved_apps,
        'rejected_loans': rejected_apps,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'approval_rate': approval_rate
    }
    
    return render_template('dashboard.html', metrics=metrics, recent_applications=recent_apps)
