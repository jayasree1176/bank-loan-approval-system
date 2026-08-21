import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

def evaluate_model_performance(y_true, y_pred, y_prob=None):
    """
    Evaluate machine learning model performance.
    Returns dictionary with all required metrics.
    """
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    auc = roc_auc_score(y_true, y_prob) if y_prob is not None else None
    cm = confusion_matrix(y_true, y_pred).tolist()
    
    metrics = {
        'accuracy': round(float(acc), 4),
        'precision': round(float(prec), 4),
        'recall': round(float(rec), 4),
        'f1_score': round(float(f1), 4),
        'roc_auc': round(float(auc), 4) if auc is not None else None,
        'confusion_matrix': cm
    }
    
    return metrics
