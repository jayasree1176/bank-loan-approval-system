/**
 * Bank Loan Approval & Credit Risk Intelligence System
 * Dynamic Form Utilities & Interactive Scripting
 */

document.addEventListener('DOMContentLoaded', function() {
    initDTIAutoCalculator();
    initIncomeCalculator();
    initTooltipSupport();
});

/**
 * Auto-calculate Monthly Income when Annual Income changes
 */
function initIncomeCalculator() {
    const annualIncomeInput = document.getElementById('annual_income');
    const monthlyIncomeInput = document.getElementById('monthly_income');
    
    if (annualIncomeInput && monthlyIncomeInput) {
        annualIncomeInput.addEventListener('input', function() {
            const annualVal = parseFloat(this.value) || 0;
            if (annualVal > 0 && (!monthlyIncomeInput.value || monthlyIncomeInput.dataset.autoCalculated === 'true')) {
                const monthlyVal = (annualVal / 12).toFixed(2);
                monthlyIncomeInput.value = monthlyVal;
                monthlyIncomeInput.dataset.autoCalculated = 'true';
                triggerDTIUpdate();
            }
        });

        monthlyIncomeInput.addEventListener('change', function() {
            this.dataset.autoCalculated = 'false';
        });
    }
}

/**
 * Auto-calculate DTI Ratio dynamically as financial inputs change
 */
function initDTIAutoCalculator() {
    const fields = ['monthly_income', 'coapplicant_income', 'loan_amount', 'loan_term', 'existing_loans'];
    
    fields.forEach(fieldId => {
        const elem = document.getElementById(fieldId);
        if (elem) {
            elem.addEventListener('input', triggerDTIUpdate);
        }
    });
}

function triggerDTIUpdate() {
    const monthlyIncome = parseFloat(document.getElementById('monthly_income')?.value) || 0;
    const coapplicantIncome = parseFloat(document.getElementById('coapplicant_income')?.value) || 0;
    const loanAmount = parseFloat(document.getElementById('loan_amount')?.value) || 0;
    const loanTerm = parseInt(document.getElementById('loan_term')?.value) || 12;
    const existingLoans = parseInt(document.getElementById('existing_loans')?.value) || 0;
    
    const dtiInput = document.getElementById('dti_ratio');
    if (!dtiInput) return;
    
    const totalMonthlyIncome = monthlyIncome + (coapplicantIncome / 12);
    if (totalMonthlyIncome <= 0 || loanAmount <= 0) {
        return;
    }
    
    const estMonthlyLoanPayment = loanAmount / Math.max(loanTerm, 1);
    const estExistingDebtPayments = existingLoans * 250;
    const totalMonthlyDebt = estMonthlyLoanPayment + estExistingDebtPayments;
    
    const calculatedDTI = ((totalMonthlyDebt / totalMonthlyIncome) * 100).toFixed(2);
    
    if (calculatedDTI > 0 && calculatedDTI <= 100) {
        dtiInput.value = Math.min(calculatedDTI, 99.9).toFixed(2);
        
        // Visual indicator border on DTI field
        if (calculatedDTI > 45) {
            dtiInput.classList.add('border-warning');
        } else {
            dtiInput.classList.remove('border-warning');
        }
    }
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltipSupport() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}
