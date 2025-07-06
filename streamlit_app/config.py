"""
Configuration pour l'application Streamlit
"""

# =====================================================
# CONFIGURATION API
# =====================================================

# URL de base de l'API FastAPI (locale par défaut)
API_BASE_URL = "http://localhost:8000"

# Endpoints de l'API
API_ENDPOINTS = {
    "predict": f"{API_BASE_URL}/predict/client",
    "health": f"{API_BASE_URL}/health",
    "model_info": f"{API_BASE_URL}/model/info", 
    "fake_client": f"{API_BASE_URL}/generate/fake-client",
    "demo": f"{API_BASE_URL}/demo/predict-fake-client",
    "profile_types": f"{API_BASE_URL}/generate/profile-types"
}

# Timeout pour les requêtes API
API_TIMEOUT = 30

# =====================================================
# CONFIGURATION STREAMLIT
# =====================================================

# Configuration de la page
PAGE_CONFIG = {
    "page_title": "🎯 Churn Prediction Dashboard",
    "page_icon": "🎯",  # Icon unique corrigé
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Thème couleurs
COLORS = {
    "success": "#28a745",
    "warning": "#ffc107", 
    "danger": "#dc3545",
    "info": "#17a2b8",
    "primary": "#007bff",
    "secondary": "#6c757d",
    "stable": "#28a745",      # Vert pour client stable
    "medium": "#ffc107",      # Orange pour medium risk  
    "high": "#dc3545"         # Rouge pour high risk
}

# =====================================================
# CONFIGURATION BUSINESS
# =====================================================

# Seuils de risque pour les couleurs
RISK_THRESHOLDS = {
    "low": 0.35,      # Seuil du modèle
    "medium": 0.65,    
    "high": 0.8
}

# Messages de recommandations par niveau de risque
RISK_MESSAGES = {
    "Critical Risk": {
        "emoji": "🚨",
        "color": COLORS["high"],
        "action": "ACTION IMMÉDIATE REQUISE"
    },
    "High Risk": {
        "emoji": "⚠️", 
        "color": COLORS["high"],
        "action": "CONTACT SOUS 48H"
    },
    "Medium-High Risk": {
        "emoji": "📞",
        "color": COLORS["warning"], 
        "action": "SURVEILLANCE RENFORCÉE"
    },
    "Medium Risk": {
        "emoji": "👀",
        "color": COLORS["warning"],
        "action": "MONITORING ACTIF"
    },
    "Low-Medium Risk": {
        "emoji": "📊",
        "color": COLORS["info"],
        "action": "SUIVI MENSUEL"
    },
    "Low Risk": {
        "emoji": "✅",
        "color": COLORS["stable"],
        "action": "CLIENT STABLE"
    }
}

# =====================================================
# CONFIGURATION FAKER
# =====================================================

# Descriptions des profils Faker
PROFILE_DESCRIPTIONS = {
    "random": {
        "name": "🎲 Aléatoire",
        "description": "Profil complètement aléatoire avec distribution réaliste",
        "color": COLORS["secondary"]
    },
    "high_risk": {
        "name": "🚨 Haut Risque", 
        "description": "Client susceptible de churner (nouveau, facture élevée)",
        "color": COLORS["danger"]
    },
    "stable": {
        "name": "✅ Stable",
        "description": "Client fidèle avec contrat long terme",
        "color": COLORS["success"]
    },
    "new": {
        "name": "🆕 Nouveau",
        "description": "Client récent (0-3 mois d'ancienneté)", 
        "color": COLORS["info"]
    },
    "premium": {
        "name": "👑 Premium",
        "description": "Client haut de gamme avec services premium",
        "color": COLORS["primary"]
    }
}

# =====================================================
# CONFIGURATION FORMULAIRE
# =====================================================

# Options pour les champs select
FORM_OPTIONS = {
    "contract": ["Month-to-month", "One year", "Two year"],
    "payment_method": [
        "Bank transfer (automatic)", 
        "Credit card (automatic)",
        "Electronic check", 
        "Mailed check"
    ],
    "internet_service": ["DSL", "Fiber optic", "No"],
    "paperless_billing": ["No", "Yes"]
}

# Valeurs par défaut du formulaire
DEFAULT_VALUES = {
    "contract": "Month-to-month",
    "tenure": 12,
    "monthly_charges": 75.0,
    "total_charges": 900.0,
    "payment_method": "Electronic check",
    "internet_service": "Fiber optic", 
    "paperless_billing": "Yes"
}

# Aide contextuelle pour les champs
FIELD_HELP = {
    "contract": "Type de contrat du client (durée d'engagement)",
    "tenure": "Ancienneté du client en mois (0 = nouveau client)",
    "monthly_charges": "Facturation mensuelle en euros (doit être > 0)",
    "total_charges": "Total facturé depuis le début (peut être 0 pour nouveau client)",
    "payment_method": "Mode de paiement utilisé par le client",
    "internet_service": "Type de service Internet souscrit",
    "paperless_billing": "Le client reçoit-il ses factures par email ?"
}

# =====================================================
# CONFIGURATION CACHE
# =====================================================

# Durée de cache pour les données API (en secondes)
CACHE_TTL = 300  # 5 minutes

# Clés de cache Streamlit
CACHE_KEYS = {
    "model_info": "model_info_cache",
    "api_health": "api_health_cache",
    "prediction_history": "prediction_history"
}