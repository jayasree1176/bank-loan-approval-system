def validate_loan_form_input(form_data):
    """
    Validate all 19 loan application input fields.
    Returns (is_valid, errors_dict, cleaned_data_dict)
    """
    errors = {}
    cleaned = {}
    
    # 1. Applicant Name
    applicant_name = form_data.get('applicant_name', '').strip()
    if not applicant_name or len(applicant_name) < 2:
        errors['applicant_name'] = "Applicant name must be at least 2 characters long."
    cleaned['applicant_name'] = applicant_name
    
    # Helper parser functions
    def parse_int(field, min_val, max_val, label):
        val = form_data.get(field, '').strip()
        try:
            val_int = int(val)
            if val_int < min_val or val_int > max_val:
                errors[field] = f"{label} must be between {min_val} and {max_val}."
            cleaned[field] = val_int
        except ValueError:
            errors[field] = f"{label} must be a valid integer."

    def parse_float(field, min_val, max_val, label):
        val = form_data.get(field, '').strip()
        try:
            val_flt = float(val)
            if val_flt < min_val or val_flt > max_val:
                errors[field] = f"{label} must be between ${min_val:,.0f} and ${max_val:,.0f}."
            cleaned[field] = val_flt
        except ValueError:
            errors[field] = f"{label} must be a valid numeric amount."

    # 2. Age
    parse_int('age', 18, 100, 'Age')
    
    # 3. Gender
    gender = form_data.get('gender', '').strip()
    if gender not in ['Male', 'Female', 'Other']:
        errors['gender'] = "Please select a valid gender option."
    cleaned['gender'] = gender
    
    # 4. Marital Status
    marital = form_data.get('marital_status', '').strip()
    if marital not in ['Single', 'Married', 'Divorced', 'Widowed']:
        errors['marital_status'] = "Please select a valid marital status."
    cleaned['marital_status'] = marital
    
    # 5. Education
    education = form_data.get('education', '').strip()
    if education not in ['Graduate', 'Not Graduate', 'Post Graduate']:
        errors['education'] = "Please select a valid education level."
    cleaned['education'] = education
    
    # 6. Employment Status
    employment = form_data.get('employment_status', '').strip()
    if employment not in ['Salaried', 'Self-Employed', 'Business', 'Unemployed']:
        errors['employment_status'] = "Please select a valid employment status."
    cleaned['employment_status'] = employment
    
    # 7 & 8. Incomes
    parse_float('annual_income', 0, 10000000, 'Annual Income')
    
    # Auto compute monthly income if missing or zero
    annual_inc = cleaned.get('annual_income', 0)
    monthly_inc_str = form_data.get('monthly_income', '').strip()
    if monthly_inc_str:
        parse_float('monthly_income', 0, 1000000, 'Monthly Income')
    else:
        cleaned['monthly_income'] = round(annual_inc / 12, 2)
        
    # 9. Coapplicant Income
    parse_float('coapplicant_income', 0, 5000000, 'Co-Applicant Income')
    
    # 10. Loan Amount
    parse_float('loan_amount', 1000, 10000000, 'Loan Amount')
    
    # 11. Loan Term
    parse_int('loan_term', 6, 480, 'Loan Term')
    
    # 12. Credit Score
    parse_int('credit_score', 300, 850, 'Credit Score')
    
    # 13. Existing Loans
    parse_int('existing_loans', 0, 20, 'Existing Loans')
    
    # 14. Savings
    parse_float('savings', 0, 10000000, 'Savings')
    
    # 15. Property Area
    prop_area = form_data.get('property_area', '').strip()
    if prop_area not in ['Urban', 'Semiurban', 'Rural']:
        errors['property_area'] = "Please select a valid property area."
    cleaned['property_area'] = prop_area
    
    # 16. DTI Ratio
    dti_str = form_data.get('dti_ratio', '').strip()
    if dti_str:
        parse_float('dti_ratio', 0, 100, 'Debt-to-Income Ratio')
    else:
        # Calculate DTI dynamically if omitted
        monthly_inc = cleaned.get('monthly_income', 1)
        co_inc = cleaned.get('coapplicant_income', 0)
        tot_inc = monthly_inc + (co_inc / 12)
        loan_amt = cleaned.get('loan_amount', 0)
        term = cleaned.get('loan_term', 12)
        exist_loans = cleaned.get('existing_loans', 0)
        
        est_payment = loan_amt / max(term, 1) + (exist_loans * 250)
        calculated_dti = round(min((est_payment / max(tot_inc, 1)) * 100, 100), 2)
        cleaned['dti_ratio'] = calculated_dti
        
    # 17. Collateral Value
    parse_float('collateral_value', 0, 20000000, 'Collateral Value')
    
    # 18. Loan Purpose
    purpose = form_data.get('loan_purpose', '').strip()
    if purpose not in ['Home Loan', 'Personal Loan', 'Auto Loan', 'Business Loan', 'Education Loan']:
        errors['loan_purpose'] = "Please select a valid loan purpose."
    cleaned['loan_purpose'] = purpose
    
    # 19. Dependents
    parse_int('dependents', 0, 15, 'Dependents')
    
    is_valid = len(errors) == 0
    return is_valid, errors, cleaned
