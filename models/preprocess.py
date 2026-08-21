import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib
import os

# Definition of feature columns
CATEGORICAL_FEATURES = [
    'gender', 'marital_status', 'education', 
    'employment_status', 'property_area', 'loan_purpose'
]

NUMERICAL_FEATURES = [
    'age', 'annual_income', 'monthly_income', 'coapplicant_income',
    'loan_amount', 'loan_term', 'credit_score', 'existing_loans',
    'savings', 'dti_ratio', 'collateral_value', 'dependents'
]

ALL_FEATURE_COLUMNS = [
    'applicant_name', 'age', 'gender', 'marital_status', 'education',
    'employment_status', 'annual_income', 'monthly_income', 'coapplicant_income',
    'loan_amount', 'loan_term', 'credit_score', 'existing_loans',
    'savings', 'property_area', 'dti_ratio', 'collateral_value',
    'loan_purpose', 'dependents'
]

def clean_data(df):
    """Clean data and fill missing values."""
    df_clean = df.copy()
    
    # Handle missing numerical values with median
    for col in NUMERICAL_FEATURES:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            df_clean[col] = df_clean[col].fillna(df_clean[col].median() if not df_clean[col].isnull().all() else 0)
            
    # Handle missing categorical values with mode
    for col in CATEGORICAL_FEATURES:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0] if len(df_clean[col].mode()) > 0 else 'Unknown')
            
    return df_clean

def get_preprocessor():
    """Create and return a scikit-learn ColumnTransformer for preprocessing."""
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), NUMERICAL_FEATURES),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES)
        ],
        remainder='drop'
    )
    return preprocessor
