-- Bank Loan Approval and Credit Risk Intelligence System Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    applicant_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    marital_status TEXT NOT NULL,
    education TEXT NOT NULL,
    employment_status TEXT NOT NULL,
    annual_income REAL NOT NULL,
    monthly_income REAL NOT NULL,
    coapplicant_income REAL NOT NULL,
    loan_amount REAL NOT NULL,
    loan_term INTEGER NOT NULL,
    credit_score INTEGER NOT NULL,
    existing_loans INTEGER NOT NULL,
    savings REAL NOT NULL,
    property_area TEXT NOT NULL,
    dti_ratio REAL NOT NULL,
    collateral_value REAL NOT NULL,
    loan_purpose TEXT NOT NULL,
    dependents INTEGER NOT NULL,
    prediction_status TEXT NOT NULL,
    approval_probability REAL NOT NULL,
    risk_level TEXT NOT NULL,
    risk_factors TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
