# Bank Loan Approval and Credit Risk Intelligence System

A full-stack, enterprise-grade web application built with **Python Flask**, **SQLite**, **Bootstrap 5**, **Chart.js**, and **Scikit-Learn Machine Learning**.

The system automates bank loan decisioning, predicts approval probability percentages, and classifies applicant credit risk levels into **Low**, **Medium**, or **High** tiers based on 19 comprehensive parameters.

---

## Folder Structure

```text
Bank-Loan-Approval-System/
│
├── app.py                      # Flask main entry point & blueprint registration
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
├── loan_model.pkl              # Saved trained Random Forest model
├── scaler.pkl                  # Saved StandardScaler & preprocessor
├── database.db                 # SQLite Database file
│
├── static/
│   ├── css/
│   │   ├── style.css           # Main banking theme & styling system
│   │   └── dashboard.css       # Sidebar & analytics layout
│   ├── js/
│   │   ├── script.js           # Form validation & DTI auto-calculator
│   │   └── charts.js           # Chart.js analytics visualizer
│   ├── images/
│   │   ├── logo.png            # Application logo
│   │   └── banner.jpg          # Hero banking banner
│   └── uploads/                # Bulk CSV upload directory
│
├── templates/
│   ├── index.html              # Landing page
│   ├── login.html              # Authentication login
│   ├── register.html           # User registration
│   ├── dashboard.html          # Underwriting & risk dashboard
│   ├── predict.html            # 19-field Loan Application Form & CSV upload
│   ├── prediction_result.html   # Detailed decision breakdown & gauge chart
│   ├── history.html            # Searchable prediction audit history
│   ├── analytics.html          # Visual charts dashboard
│   ├── admin.html              # Admin panel & user management
│   ├── profile.html            # User profile settings
│   ├── about.html              # Architecture & ML specs
│   └── error.html              # Custom 404/500 page
│
├── models/
│   ├── train_model.py          # Synthetic dataset generation & RF model trainer
│   ├── prediction.py           # Model inference engine
│   ├── preprocess.py           # Data cleaner & preprocessor
│   └── evaluate.py             # Accuracy, F1, ROC-AUC metric evaluator
│
├── database/
│   ├── database.py             # SQLite helper connection pool
│   ├── schema.sql              # SQL DDL for users and applications
│   └── seed_data.py            # Sample seed script
│
├── routes/
│   ├── auth.py                 # Login, Register, Profile routes
│   ├── prediction.py           # Single & bulk prediction endpoints
│   ├── dashboard.py            # Dashboard metrics loader
│   ├── analytics.py            # Chart.js JSON APIs
│   └── admin.py                # Admin security control panel
│
├── utils/
│   ├── helper.py               # Session decorators & currency formatters
│   ├── validation.py           # 19-field form input validator
│   └── feature_engineering.py  # DTI ratio & credit score calculators
│
├── dataset/
│   ├── loan_dataset.csv        # Synthetic dataset (1,200 records)
│   └── processed_dataset.csv   # Encoded training dataset
│
└── notebooks/
    └── model_training.ipynb    # Documented Jupyter Notebook
```

---

## 🚀 Quick Setup & Execution

### 1. Install Dependencies
```bash
cd Bank-Loan-Approval-System
pip install -r requirements.txt
```

### 2. Train Model & Seed Database
```bash
python models/train_model.py
python database/seed_data.py
```

### 3. Launch Web Application
```bash
python app.py
```
Open your browser at **http://127.0.0.1:5000**

---

## 🔑 Demo Account Credentials

| Account Role | Username | Password |
|---|---|---|
| **Admin User** | `admin` | `admin123` |
| **Loan Officer** | `loan_officer` | `password123` |

---

## 📋 19 Loan Application Fields
1. Applicant Name
2. Age
3. Gender
4. Marital Status
5. Education
6. Employment Status
7. Annual Income
8. Monthly Income
9. Co-Applicant Income
10. Loan Amount
11. Loan Term (Months)
12. Credit Score (300-850)
13. Existing Active Loans
14. Savings
15. Property Area (Urban/Semiurban/Rural)
16. Debt-to-Income (DTI) Ratio (%)
17. Collateral Value ($)
18. Loan Purpose
19. Dependents Count
