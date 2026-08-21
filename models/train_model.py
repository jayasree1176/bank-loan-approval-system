import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

from models.preprocess import clean_data, get_preprocessor, NUMERICAL_FEATURES, CATEGORICAL_FEATURES
from models.evaluate import evaluate_model_performance

def generate_synthetic_loan_dataset(n_samples=1200, random_state=42):
    """Generate realistic loan dataset for credit risk modeling."""
    np.random.seed(random_state)
    
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
                   "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Charles", "Karen", "Rahul", "Priya", "Amit", "Ananya", "Carlos"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Sharma", "Verma"]
    
    names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(n_samples)]
    
    age = np.random.randint(21, 68, size=n_samples)
    gender = np.random.choice(["Male", "Female"], size=n_samples, p=[0.55, 0.45])
    marital_status = np.random.choice(["Single", "Married", "Divorced"], size=n_samples, p=[0.4, 0.5, 0.1])
    education = np.random.choice(["Graduate", "Not Graduate", "Post Graduate"], size=n_samples, p=[0.6, 0.25, 0.15])
    employment_status = np.random.choice(["Salaried", "Self-Employed", "Business", "Unemployed"], size=n_samples, p=[0.55, 0.25, 0.15, 0.05])
    
    # Financial metrics
    annual_income = np.random.exponential(scale=45000, size=n_samples) + 20000
    annual_income = np.round(annual_income, -2)
    monthly_income = np.round(annual_income / 12, 2)
    coapplicant_income = np.where(marital_status == "Married", np.random.exponential(scale=20000, size=n_samples), 0)
    coapplicant_income = np.round(coapplicant_income, -2)
    
    credit_score = np.random.normal(loc=680, scale=80, size=n_samples)
    credit_score = np.clip(np.round(credit_score), 300, 850).astype(int)
    
    loan_amount = np.random.normal(loc=180000, scale=90000, size=n_samples)
    loan_amount = np.clip(np.round(loan_amount, -3), 10000, 750000)
    
    loan_term = np.random.choice([12, 24, 36, 48, 60, 120, 180, 240, 360], size=n_samples, p=[0.05, 0.05, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.2])
    existing_loans = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.4, 0.35, 0.15, 0.07, 0.03])
    savings = np.round(np.random.exponential(scale=30000, size=n_samples), -2)
    
    property_area = np.random.choice(["Urban", "Semiurban", "Rural"], size=n_samples, p=[0.45, 0.35, 0.20])
    loan_purpose = np.random.choice(["Home Loan", "Personal Loan", "Auto Loan", "Business Loan", "Education Loan"], size=n_samples, p=[0.35, 0.25, 0.15, 0.15, 0.10])
    dependents = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.45, 0.25, 0.2, 0.07, 0.03])
    
    # Calculate DTI Ratio and Collateral
    total_income = monthly_income + (coapplicant_income / 12)
    est_monthly_debt = (loan_amount / loan_term) + (existing_loans * 300)
    dti_ratio = np.round(np.clip((est_monthly_debt / np.maximum(total_income, 1000)) * 100, 5, 85), 2)
    
    collateral_value = np.where(np.isin(loan_purpose, ["Home Loan", "Auto Loan", "Business Loan"]), loan_amount * np.random.uniform(0.8, 1.8, size=n_samples), loan_amount * np.random.uniform(0.1, 0.6, size=n_samples))
    collateral_value = np.round(collateral_value, -2)
    
    # Realistic Credit Risk / Approval Logic to create ground truth label
    # High credit score, low DTI, high income, good collateral -> higher approval chance
    score = (
        (credit_score - 300) / 550 * 0.35 +
        np.clip(collateral_value / loan_amount, 0, 2) * 0.20 +
        (1 - np.clip(dti_ratio / 80, 0, 1)) * 0.25 +
        np.clip((annual_income + coapplicant_income) / loan_amount, 0, 2) * 0.15 +
        np.where(np.isin(employment_status, ["Salaried", "Business"]), 0.05, 0)
    )
    
    # Add random realistic noise
    score += np.random.normal(0, 0.08, size=n_samples)
    loan_status = np.where(score >= 0.52, 1, 0) # 1 = Approved, 0 = Rejected
    
    df = pd.DataFrame({
        'applicant_name': names,
        'age': age,
        'gender': gender,
        'marital_status': marital_status,
        'education': education,
        'employment_status': employment_status,
        'annual_income': annual_income,
        'monthly_income': monthly_income,
        'coapplicant_income': coapplicant_income,
        'loan_amount': loan_amount,
        'loan_term': loan_term,
        'credit_score': credit_score,
        'existing_loans': existing_loans,
        'savings': savings,
        'property_area': property_area,
        'dti_ratio': dti_ratio,
        'collateral_value': collateral_value,
        'loan_purpose': loan_purpose,
        'dependents': dependents,
        'loan_status': loan_status
    })
    
    return df

def train_and_save_model():
    """Build dataset, train Random Forest classifier, evaluate, and save artifacts."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dataset_dir = os.path.join(base_dir, 'dataset')
    os.makedirs(dataset_dir, exist_ok=True)
    
    raw_dataset_path = os.path.join(dataset_dir, 'loan_dataset.csv')
    processed_dataset_path = os.path.join(dataset_dir, 'processed_dataset.csv')
    
    print("Generating synthetic dataset...")
    df = generate_synthetic_loan_dataset(n_samples=1200)
    df.to_csv(raw_dataset_path, index=False)
    print(f"Saved raw dataset to: {raw_dataset_path}")
    
    df_clean = clean_data(df)
    
    X = df_clean.drop(columns=['applicant_name', 'loan_status'])
    y = df_clean['loan_status']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Fitting feature scaling & encoding preprocessor...")
    preprocessor = get_preprocessor()
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)
    
    # Save processed training dataset for notebook / reference
    processed_df = pd.DataFrame(X_train_transformed)
    processed_df['loan_status'] = y_train.values
    processed_df.to_csv(processed_dataset_path, index=False)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_transformed, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_transformed)
    y_prob = model.predict_proba(X_test_transformed)[:, 1]
    
    metrics = evaluate_model_performance(y_test, y_pred, y_prob)
    
    print("\n--- Model Evaluation Results ---")
    print(f"Accuracy : {metrics['accuracy'] * 100:.2f}%")
    print(f"Precision: {metrics['precision'] * 100:.2f}%")
    print(f"Recall   : {metrics['recall'] * 100:.2f}%")
    print(f"F1 Score : {metrics['f1_score'] * 100:.2f}%")
    print(f"ROC AUC  : {metrics['roc_auc'] * 100:.2f}%")
    print(f"Confusion Matrix: {metrics['confusion_matrix']}")
    print("--------------------------------\n")
    
    # Save artifacts to root project directory
    model_path = os.path.join(base_dir, 'loan_model.pkl')
    scaler_path = os.path.join(base_dir, 'scaler.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(preprocessor, scaler_path)
    
    print(f"Model saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")
    return metrics

if __name__ == '__main__':
    train_and_save_model()
