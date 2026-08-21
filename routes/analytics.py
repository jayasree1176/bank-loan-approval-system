from flask import Blueprint, render_template, jsonify, session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.database import query_db
from utils.helper import login_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def index():
    return render_template('analytics.html')

@analytics_bp.route('/api/analytics-data')
@login_required
def get_analytics_data():
    user_id = session['user_id']
    role = session.get('role')
    
    where_clause = "" if role == 'admin' else f"WHERE user_id = {user_id}"
    
    # 1. Status Breakdown
    approved = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} prediction_status = 'Approved'", one=True)['cnt']
    rejected = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} prediction_status = 'Rejected'", one=True)['cnt']
    
    # 2. Risk Distribution
    low_risk = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} risk_level = 'Low'", one=True)['cnt']
    med_risk = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} risk_level = 'Medium'", one=True)['cnt']
    high_risk = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} risk_level = 'High'", one=True)['cnt']
    
    # 3. Credit Score Ranges
    score_300_599 = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} credit_score < 600", one=True)['cnt']
    score_600_679 = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} credit_score BETWEEN 600 AND 679", one=True)['cnt']
    score_680_739 = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} credit_score BETWEEN 680 AND 739", one=True)['cnt']
    score_740_799 = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} credit_score BETWEEN 740 AND 799", one=True)['cnt']
    score_800_850 = query_db(f"SELECT COUNT(*) as cnt FROM applications {where_clause} {'AND' if where_clause else 'WHERE'} credit_score >= 800", one=True)['cnt']
    
    # 4. Loan Purpose Breakdown
    purposes_rows = query_db(f"SELECT loan_purpose, COUNT(*) as cnt FROM applications {where_clause} GROUP BY loan_purpose")
    purposes = {row['loan_purpose']: row['cnt'] for row in purposes_rows}
    
    # 5. Monthly Applications Trend
    monthly_rows = query_db(f"SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as cnt FROM applications {where_clause} GROUP BY month ORDER BY month ASC LIMIT 12")
    monthly_labels = [row['month'] or 'Current' for row in monthly_rows]
    monthly_counts = [row['cnt'] for row in monthly_rows]
    
    if not monthly_labels:
        monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        monthly_counts = [12, 19, 15, 25, 22, 30]

    response = {
        'status_distribution': {
            'approved': approved,
            'rejected': rejected
        },
        'risk_distribution': {
            'low': low_risk,
            'medium': med_risk,
            'high': high_risk
        },
        'credit_score_distribution': {
            '300-599': score_300_599,
            '600-679': score_600_679,
            '680-739': score_680_739,
            '740-799': score_740_799,
            '800-850': score_800_850
        },
        'loan_purposes': purposes,
        'monthly_trends': {
            'labels': monthly_labels,
            'counts': monthly_counts
        }
    }
    
    return jsonify(response)
