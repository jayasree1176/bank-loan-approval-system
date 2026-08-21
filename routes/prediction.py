from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, Response, current_app
import json
import pandas as pd
import io
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.database import query_db, execute_db
from models.prediction import LoanPredictor
from utils.validation import validate_loan_form_input
from utils.helper import login_required

predict_bp = Blueprint('predict', __name__)
predictor = LoanPredictor()

@predict_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        is_valid, errors, cleaned_data = validate_loan_form_input(request.form)
        
        if not is_valid:
            for field, err in errors.items():
                flash(f"{err}", "danger")
            return render_template('predict.html', form_data=request.form, errors=errors)
            
        # Perform machine learning inference
        result = predictor.predict_single(cleaned_data)
        
        user_id = session['user_id']
        
        # Save to SQLite database
        app_id = execute_db(
            """INSERT INTO applications (
                user_id, applicant_name, age, gender, marital_status, education, employment_status,
                annual_income, monthly_income, coapplicant_income, loan_amount, loan_term,
                credit_score, existing_loans, savings, property_area, dti_ratio, collateral_value,
                loan_purpose, dependents, prediction_status, approval_probability, risk_level, risk_factors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                cleaned_data['applicant_name'],
                cleaned_data['age'],
                cleaned_data['gender'],
                cleaned_data['marital_status'],
                cleaned_data['education'],
                cleaned_data['employment_status'],
                cleaned_data['annual_income'],
                cleaned_data['monthly_income'],
                cleaned_data['coapplicant_income'],
                cleaned_data['loan_amount'],
                cleaned_data['loan_term'],
                cleaned_data['credit_score'],
                cleaned_data['existing_loans'],
                cleaned_data['savings'],
                cleaned_data['property_area'],
                cleaned_data['dti_ratio'],
                cleaned_data['collateral_value'],
                cleaned_data['loan_purpose'],
                cleaned_data['dependents'],
                result['status'],
                result['approval_probability'],
                result['risk_level'],
                json.dumps(result['risk_factors'])
            )
        )
        
        # Log system action
        execute_db("INSERT INTO system_logs (user_id, action) VALUES (?, ?)", (user_id, f"Evaluated loan application #{app_id} for {cleaned_data['applicant_name']}"))
        
        flash("Loan evaluation completed!", "success")
        return redirect(url_for('predict.prediction_result', app_id=app_id))
        
    return render_template('predict.html', form_data={}, errors={})

@predict_bp.route('/predict/bulk', methods=['POST'])
@login_required
def predict_bulk():
    if 'csv_file' not in request.files:
        flash("No CSV file selected.", "danger")
        return redirect(url_for('predict.predict'))
        
    file = request.files['csv_file']
    if file.filename == '':
        flash("No selected file.", "danger")
        return redirect(url_for('predict.predict'))
        
    if not file.filename.lower().endswith('.csv'):
        flash("Only CSV files are supported for bulk predictions.", "danger")
        return redirect(url_for('predict.predict'))
        
    try:
        df_upload = pd.read_csv(file)
        
        required_cols = [
            'applicant_name', 'age', 'gender', 'marital_status', 'education',
            'employment_status', 'annual_income', 'monthly_income', 'coapplicant_income',
            'loan_amount', 'loan_term', 'credit_score', 'existing_loans',
            'savings', 'property_area', 'dti_ratio', 'collateral_value',
            'loan_purpose', 'dependents'
        ]
        
        # Ensure missing columns get default values
        for col in required_cols:
            if col not in df_upload.columns:
                if col in ['age', 'loan_term', 'credit_score', 'existing_loans', 'dependents']:
                    df_upload[col] = 0
                elif col in ['annual_income', 'monthly_income', 'coapplicant_income', 'loan_amount', 'savings', 'dti_ratio', 'collateral_value']:
                    df_upload[col] = 0.0
                else:
                    df_upload[col] = 'Unknown'
                    
        df_results = predictor.predict_bulk(df_upload)
        user_id = session['user_id']
        
        # Save records to DB
        for _, row in df_results.iterrows():
            execute_db(
                """INSERT INTO applications (
                    user_id, applicant_name, age, gender, marital_status, education, employment_status,
                    annual_income, monthly_income, coapplicant_income, loan_amount, loan_term,
                    credit_score, existing_loans, savings, property_area, dti_ratio, collateral_value,
                    loan_purpose, dependents, prediction_status, approval_probability, risk_level, risk_factors
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id, str(row.get('applicant_name', 'Bulk Applicant')), int(row.get('age', 30)),
                    str(row.get('gender', 'Male')), str(row.get('marital_status', 'Single')),
                    str(row.get('education', 'Graduate')), str(row.get('employment_status', 'Salaried')),
                    float(row.get('annual_income', 50000)), float(row.get('monthly_income', 4166)),
                    float(row.get('coapplicant_income', 0)), float(row.get('loan_amount', 100000)),
                    int(row.get('loan_term', 120)), int(row.get('credit_score', 650)),
                    int(row.get('existing_loans', 0)), float(row.get('savings', 10000)),
                    str(row.get('property_area', 'Urban')), float(row.get('dti_ratio', 35)),
                    float(row.get('collateral_value', 100000)), str(row.get('loan_purpose', 'Personal Loan')),
                    int(row.get('dependents', 0)), str(row['prediction_status']),
                    float(row['approval_probability']), str(row['risk_level']),
                    json.dumps(["Bulk CSV process evaluation"])
                )
            )
            
        execute_db("INSERT INTO system_logs (user_id, action) VALUES (?, ?)", (user_id, f"Bulk processed CSV with {len(df_results)} records"))
        flash(f"Successfully processed {len(df_results)} records from CSV!", "success")
        return redirect(url_for('predict.history'))
        
    except Exception as e:
        flash(f"Error processing CSV file: {str(e)}", "danger")
        return redirect(url_for('predict.predict'))

@predict_bp.route('/prediction/<int:app_id>')
@login_required
def prediction_result(app_id):
    user_id = session['user_id']
    role = session.get('role')
    
    if role == 'admin':
        app_data = query_db("SELECT * FROM applications WHERE id = ?", (app_id,), one=True)
    else:
        app_data = query_db("SELECT * FROM applications WHERE id = ? AND user_id = ?", (app_id, user_id), one=True)
        
    if not app_data:
        flash("Application record not found.", "danger")
        return redirect(url_for('predict.history'))
        
    risk_factors = []
    if app_data['risk_factors']:
        try:
            risk_factors = json.loads(app_data['risk_factors'])
        except Exception:
            risk_factors = [app_data['risk_factors']]
            
    return render_template('prediction_result.html', app=app_data, risk_factors=risk_factors)

@predict_bp.route('/history')
@login_required
def history():
    user_id = session['user_id']
    role = session.get('role')
    
    search = request.args.get('search', '').strip()
    risk_filter = request.args.get('risk', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = "SELECT * FROM applications WHERE 1=1"
    params = []
    
    if role != 'admin':
        query += " AND user_id = ?"
        params.append(user_id)
        
    if search:
        query += " AND (applicant_name LIKE ? OR loan_purpose LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
        
    if risk_filter:
        query += " AND risk_level = ?"
        params.append(risk_filter)
        
    if status_filter:
        query += " AND prediction_status = ?"
        params.append(status_filter)
        
    query += " ORDER BY created_at DESC"
    
    applications = query_db(query, params)
    return render_template('history.html', applications=applications, search=search, risk_filter=risk_filter, status_filter=status_filter)

@predict_bp.route('/download/csv')
@login_required
def download_csv():
    user_id = session['user_id']
    role = session.get('role')
    
    if role == 'admin':
        apps = query_db("SELECT * FROM applications ORDER BY created_at DESC")
    else:
        apps = query_db("SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        
    df = pd.DataFrame([dict(row) for row in apps])
    
    output = io.StringIO()
    df.to_csv(output, index=False)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=loan_predictions_export.csv"}
    )
