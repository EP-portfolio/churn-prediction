"""
Configuration centralisée du projet churn prediction - Version Streamlit Cloud
"""
import os
from pathlib import Path

# === CHEMINS DES FICHIERS (adaptés pour streamlit_cloud) ===
PROJECT_ROOT = Path(__file__).parent.parent  # streamlit_cloud/
MODELS_DIR = PROJECT_ROOT / "models"
ENCODERS_DIR = PROJECT_ROOT / "encoders"

# === ARTEFACTS MODÈLE ===
MODEL_PATH = MODELS_DIR / "xgboost_champion_optimized.pkl"
THRESHOLD_PATH = MODELS_DIR / "optimal_threshold.pkl"
HYPERPARAMS_PATH = MODELS_DIR / "best_hyperparams_optimized.json"
METRICS_PATH = MODELS_DIR / "final_metrics_optimized.json"

# === ENCODERS REQUIS ===
ENCODER_FILES = {
    'Contract': ENCODERS_DIR / "labelencoder_Contract.pkl",
    'PaymentMethod': ENCODERS_DIR / "labelencoder_PaymentMethod.pkl", 
    'InternetService': ENCODERS_DIR / "labelencoder_InternetService.pkl",
    'PaperlessBilling': ENCODERS_DIR / "labelencoder_PaperlessBilling.pkl"
}

# === MAPPINGS FEATURES CATÉGORIELLES ===
CONTRACT_VALUES = ['Month-to-month', 'One year', 'Two year']
PAYMENT_METHOD_VALUES = ['Bank transfer (automatic)', 'Credit card (automatic)', 
                        'Electronic check', 'Mailed check']
INTERNET_SERVICE_VALUES = ['DSL', 'Fiber optic', 'No']
PAPERLESS_BILLING_VALUES = ['No', 'Yes']

# === TENURE SEGMENTS ===
TENURE_SEGMENT_MAPPING = {
    'Nouveaux_0-6m': 0,
    'Junior_6-12m': 1,
    'Moyen_12-24m': 2,
    'Senior_24m+': 3
}

TENURE_BINS = [-1, 6, 12, 24, 100]
TENURE_LABELS = ['Nouveaux_0-6m', 'Junior_6-12m', 'Moyen_12-24m', 'Senior_24m+']

# === FEATURES DU MODÈLE (ordre exact) ===
MODEL_FEATURES = [
    'Ratio_MonthlyCharges_tenure',
    'Contract', 
    'tenure',
    'MonthlyCharges',
    'tenure_segment_encoded',
    'TotalCharges',
    'is_new_customer',
    'PaymentMethod',
    'InternetService', 
    'PaperlessBilling',
    'Ratio_TotalCharges_MonthlyCharges*tenure'
]

# === VALIDATION CONTRAINTES ===
MIN_TENURE = 0
MIN_MONTHLY_CHARGES = 0.01  # > 0
MIN_TOTAL_CHARGES = 0       # >= 0

# === CONFIGURATION STREAMLIT ===
STREAMLIT_CONFIG = {
    "page_title": "Churn Prediction Dashboard",
    "page_icon": "🎯",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# === CONFIGURATION FAKER ===
FAKER_PROFILES = {
    "random": {
        "name": "🎲 Aléatoire",
        "description": "Profil complètement aléatoire avec distribution réaliste"
    },
    "high_risk": {
        "name": "🚨 Haut Risque", 
        "description": "Client susceptible de churner (nouveau, facture élevée)"
    },
    "stable": {
        "name": "✅ Stable",
        "description": "Client fidèle avec contrat long terme"
    },
    "new": {
        "name": "🆕 Nouveau",
        "description": "Client récent (0-3 mois d'ancienneté)"
    },
    "premium": {
        "name": "👑 Premium",
        "description": "Client haut de gamme avec services premium"
    }
}