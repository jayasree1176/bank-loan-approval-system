import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import joblib
from models.preprocess import clean_data

class LoanPredictor:
    def __init__(self, model_path=None, scaler_path=None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.model_path = model_path or os.path.join(base_dir, 'loan_model.pkl')
        self.scaler_path = scaler_path or os.path.join(base_dir, 'scaler.pkl')
        self.model = None
        self.scaler = None
        self._load_artifacts()

    def _load_artifacts(self):
        """Load trained model and scaler preprocessor."""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            # Fallback trigger model training if artifacts don't exist yet
            from models.train_model import train_and_save_model
            train_and_save_model()
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)

    def determine_risk_level(self, risk_prob):
        """
        Classify credit risk level based on risk probability (1 - approval_prob).
        Risk Prob < 0.30 -> Low Risk
        0.30 <= Risk Prob <= 0.65 -> Medium Risk
        Risk Prob > 0.65 -> High Risk
        """
        if risk_prob < 0.30:
            return "Low"
        elif risk_prob <= 0.65:
            return "Medium"
        else:
            return "High"

    def predict_single(self, input_dict):
        """
        Predict loan approval and credit risk for a single applicant dictionary.
        Returns dict with decision, probabilities, risk level, and key risk factors.
        """
        df_input = pd.DataFrame([input_dict])
        df_cleaned = clean_data(df_input)
        
        # Transform input using preprocessor
        X_transformed = self.scaler.transform(df_cleaned)
        
        # Predict class and probabilities
        prediction = self.model.predict(X_transformed)[0]
        prob_array = self.model.predict_proba(X_transformed)[0]
        
        approval_probability = float(prob_array[1]) * 100 # Percentage
        rejection_probability = float(prob_array[0]) * 100
        risk_prob = float(prob_array[0]) # 0 to 1 scale for risk evaluation
        
        status = "Approved" if prediction == 1 else "Rejected"
        risk_level = self.determine_risk_level(risk_prob)
        
        # Identify key risk factors & recommendations
        risk_factors = []
        recommendations = []
        
        credit_score = float(input_dict.get('credit_score', 650))
        dti_ratio = float(input_dict.get('dti_ratio', 40))
        annual_income = float(input_dict.get('annual_income', 50000))
        loan_amount = float(input_dict.get('loan_amount', 100000))
        collateral_value = float(input_dict.get('collateral_value', 0))
        savings = float(input_dict.get('savings', 0))
        existing_loans = int(input_dict.get('existing_loans', 0))

        if credit_score < 620:
            risk_factors.append(f"Low credit score ({int(credit_score)}) below recommended threshold of 650.")
            recommendations.append("Improve credit score by settling past overdue accounts and keeping credit card utilization low.")
        
        if dti_ratio > 45:
            risk_factors.append(f"High Debt-to-Income (DTI) ratio of {dti_ratio:.1f}%.")
            recommendations.append("Reduce monthly debt obligations before applying for new credit.")
            
        if loan_amount > (annual_income * 4):
            risk_factors.append("Requested loan amount is significantly higher than annual income leverage.")
            recommendations.append("Consider requesting a lower loan principal or extending the loan tenure.")
            
        if collateral_value < (loan_amount * 0.7):
            risk_factors.append("Collateral security value provided is insufficient relative to loan amount.")
            recommendations.append("Pledge additional collateral or add a creditworthy guarantor.")

        if savings < (loan_amount * 0.1):
            risk_factors.append("Applicant liquid savings cushion is limited.")

        if not risk_factors:
            risk_factors.append("Financial profile shows strong liquidity and favorable debt service coverage.")
            recommendations.append("Applicant meets standard underwriting criteria.")

        result = {
            'status': status,
            'approval_probability': round(approval_probability, 2),
            'rejection_probability': round(rejection_probability, 2),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': recommendations
        }
        return result

    def predict_bulk(self, df_records):
        """Bulk prediction for dataframe of applicants."""
        df_cleaned = clean_data(df_records)
        X_transformed = self.scaler.transform(df_cleaned)
        
        predictions = self.model.predict(X_transformed)
        probabilities = self.model.predict_proba(X_transformed)
        
        results = []
        for idx, row in df_records.iterrows():
            prob_approve = float(probabilities[idx][1]) * 100
            prob_reject = float(probabilities[idx][0])
            status = "Approved" if predictions[idx] == 1 else "Rejected"
            risk_level = self.determine_risk_level(prob_reject)
            
            row_dict = row.to_dict()
            row_dict['prediction_status'] = status
            row_dict['approval_probability'] = round(prob_approve, 2)
            row_dict['risk_level'] = risk_level
            results.append(row_dict)
            
        return pd.DataFrame(results)
