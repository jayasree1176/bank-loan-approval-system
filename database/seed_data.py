import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
import json

try:
    from database.database import init_db, execute_db, query_db
except ImportError:
    from database import init_db, execute_db, query_db

def seed_database():
    """Seed initial database with admin, default user, and sample applications."""
    init_db()
    
    # Check if users exist
    existing_users = query_db("SELECT COUNT(*) as count FROM users", one=True)
    if existing_users['count'] > 0:
        print("Database already contains users. Skipping seed.")
        return
        
    print("Seeding database with default users and sample loan records...")
    
    # Insert Admin User
    admin_pass = generate_password_hash("admin123")
    admin_id = execute_db(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ("admin", "admin@bankloan.com", admin_pass, "admin")
    )
    
    # Insert Standard Loan Officer User
    user_pass = generate_password_hash("password123")
    user_id = execute_db(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ("loan_officer", "officer@bankloan.com", user_pass, "user")
    )
    
    # Sample Applications
    samples = [
        (user_id, "Arthur Pendelton", 42, "Male", "Married", "Graduate", "Salaried", 95000, 7916.67, 25000, 250000, 360, 745, 1, 45000, "Semiurban", 24.5, 320000, "Home Loan", 2, "Approved", 88.50, "Low", json.dumps(["Excellent credit score (745)", "Sufficient collateral coverage"])),
        (user_id, "Sophia Sterling", 29, "Female", "Single", "Graduate", "Self-Employed", 52000, 4333.33, 0, 180000, 180, 615, 2, 8500, "Urban", 48.2, 120000, "Personal Loan", 0, "Rejected", 32.40, "High", json.dumps(["Credit score below 650", "High DTI ratio of 48.2%"])),
        (user_id, "Marcus Vance", 36, "Male", "Married", "Post Graduate", "Business", 140000, 11666.67, 35000, 450000, 240, 790, 0, 120000, "Urban", 18.2, 600000, "Business Loan", 1, "Approved", 94.20, "Low", json.dumps(["High liquid assets", "Strong business collateral"])),
        (user_id, "Elena Rostova", 31, "Female", "Single", "Graduate", "Salaried", 64000, 5333.33, 0, 120000, 120, 670, 1, 15000, "Rural", 34.0, 140000, "Auto Loan", 0, "Approved", 71.80, "Medium", json.dumps(["Moderate debt burden", "Stable employment history"])),
        (user_id, "David Miller", 50, "Male", "Divorced", "Not Graduate", "Unemployed", 22000, 1833.33, 0, 150000, 120, 540, 3, 2000, "Rural", 68.5, 30000, "Personal Loan", 2, "Rejected", 12.10, "High", json.dumps(["Low credit score (540)", "Excessive debt-to-income ratio"]))
    ]
    
    for sample in samples:
        execute_db(
            """INSERT INTO applications (
                user_id, applicant_name, age, gender, marital_status, education, employment_status,
                annual_income, monthly_income, coapplicant_income, loan_amount, loan_term,
                credit_score, existing_loans, savings, property_area, dti_ratio, collateral_value,
                loan_purpose, dependents, prediction_status, approval_probability, risk_level, risk_factors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            sample
        )
        
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
