def calculate_dti_ratio(monthly_income, coapplicant_income, loan_amount, loan_term, existing_loans):
    """Calculate Debt-to-Income (DTI) Ratio percentage."""
    total_monthly_income = monthly_income + (coapplicant_income / 12.0)
    if total_monthly_income <= 0:
        return 99.9
        
    est_monthly_loan_installment = loan_amount / max(loan_term, 1)
    est_existing_monthly_obligations = existing_loans * 250.0
    
    total_monthly_debt = est_monthly_loan_installment + est_existing_monthly_obligations
    dti = (total_monthly_debt / total_monthly_income) * 100.0
    return round(min(dti, 100.0), 2)

def calculate_loan_to_value(loan_amount, collateral_value):
    """Calculate Loan-to-Value (LTV) ratio."""
    if collateral_value <= 0:
        return 100.0
    ltv = (loan_amount / collateral_value) * 100.0
    return round(ltv, 2)

def categorize_credit_score(score):
    """Return human-readable credit score rating."""
    if score >= 750:
        return "Excellent"
    elif score >= 700:
        return "Good"
    elif score >= 650:
        return "Fair"
    elif score >= 600:
        return "Poor"
    else:
        return "Very Poor"
