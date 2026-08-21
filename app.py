from flask import Flask, render_template, session, redirect, url_for
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.database import init_db
from routes.auth import auth_bp
from routes.prediction import predict_bp
from routes.dashboard import dashboard_bp
from routes.analytics import analytics_bp
from routes.admin import admin_bp
from utils.helper import format_currency, format_date

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bank_loan_intelligence_super_secret_key_2026')

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(admin_bp)

# Register Jinja Filters
app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['format_date'] = format_date

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="The requested page could not be found."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, message="An internal server error occurred."), 500

if __name__ == '__main__':
    # Initialize DB schema if needed
    init_db()
    print("Starting Bank Loan Approval & Credit Risk Intelligence System...")
    app.run(host='0.0.0.0', port=5000, debug=True)
