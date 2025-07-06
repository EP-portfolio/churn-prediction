"""
Modèles Pydantic pour l'API de prédiction de churn
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from config.settings import (
    CONTRACT_VALUES,
    PAYMENT_METHOD_VALUES, 
    INTERNET_SERVICE_VALUES,
    PAPERLESS_BILLING_VALUES,
    MIN_TENURE,
    MIN_MONTHLY_CHARGES,
    MIN_TOTAL_CHARGES
)

class ClientInputAPI(BaseModel):
    """Modèle pour les données d'entrée client via API"""
    
    contract: str = Field(
        ..., 
        description="Type de contrat",
        example="Month-to-month"
    )
    tenure: int = Field(
        ..., 
        ge=MIN_TENURE, 
        description="Ancienneté en mois",
        example=12
    )
    monthly_charges: float = Field(
        ..., 
        gt=MIN_MONTHLY_CHARGES, 
        description="Facturation mensuelle en euros",
        example=75.50
    )
    total_charges: float = Field(
        ..., 
        ge=MIN_TOTAL_CHARGES, 
        description="Total facturé en euros",
        example=906.00
    )
    payment_method: str = Field(
        ..., 
        description="Mode de paiement",
        example="Electronic check"
    )
    internet_service: str = Field(
        ..., 
        description="Service Internet",
        example="Fiber optic"
    )
    paperless_billing: str = Field(
        ..., 
        description="Facturation numérique",
        example="Yes"
    )
    
    # Champ optionnel pour identifier le client
    client_id: Optional[str] = Field(
        None,
        description="Identifiant optionnel du client",
        example="client_12345"
    )
    
    @validator('contract')
    def validate_contract(cls, v):
        if v not in CONTRACT_VALUES:
            raise ValueError(f"Contract doit être dans {CONTRACT_VALUES}")
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in PAYMENT_METHOD_VALUES:
            raise ValueError(f"PaymentMethod doit être dans {PAYMENT_METHOD_VALUES}")
        return v
    
    @validator('internet_service')
    def validate_internet_service(cls, v):
        if v not in INTERNET_SERVICE_VALUES:
            raise ValueError(f"InternetService doit être dans {INTERNET_SERVICE_VALUES}")
        return v
    
    @validator('paperless_billing')
    def validate_paperless_billing(cls, v):
        if v not in PAPERLESS_BILLING_VALUES:
            raise ValueError(f"PaperlessBilling doit être dans {PAPERLESS_BILLING_VALUES}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "contract": "Month-to-month",
                "tenure": 12,
                "monthly_charges": 75.50,
                "total_charges": 906.00,
                "payment_method": "Electronic check",
                "internet_service": "Fiber optic",
                "paperless_billing": "Yes",
                "client_id": "client_demo_001"
            }
        }

class PredictionResponse(BaseModel):
    """Modèle pour la réponse de prédiction"""
    
    # Résultats principaux
    churn_probability: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Probabilité de churn [0-1]"
    )
    churn_prediction: int = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Prédiction binaire (0=stable, 1=churn)"
    )
    risk_level: str = Field(
        ..., 
        description="Niveau de risque interprété"
    )
    business_recommendation: str = Field(
        ..., 
        description="Recommandation d'action business"
    )
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Score de confiance de la prédiction"
    )
    
    # Métadonnées
    client_id: Optional[str] = Field(
        None, 
        description="Identifiant du client"
    )
    prediction_timestamp: str = Field(
        ..., 
        description="Horodatage de la prédiction"
    )
    
    # Informations techniques (optionnelles pour debug)
    model_metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Métadonnées techniques du modèle"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "churn_probability": 0.7834,
                "churn_prediction": 1,
                "risk_level": "High Risk",
                "business_recommendation": "⚠️ PRIORITÉ ÉLEVÉE: Contact sous 48h + analyse besoins client",
                "confidence_score": 0.89,
                "client_id": "client_demo_001",
                "prediction_timestamp": "2024-01-15T14:30:00",
                "model_metadata": {
                    "optimal_threshold": 0.3510,
                    "model_version": "XGBoost_Champion_11_Features"
                }
            }
        }

class HealthResponse(BaseModel):
    """Modèle pour la réponse de health check"""
    
    status: str = Field(..., description="Status général du service")
    model_loaded: bool = Field(..., description="Modèle chargé correctement")
    threshold_loaded: bool = Field(..., description="Seuil optimal chargé")
    preprocessor_ready: bool = Field(..., description="Preprocessor prêt")
    timestamp: str = Field(..., description="Horodatage du check")
    
    # Tests optionnels
    test_prediction_success: Optional[bool] = Field(
        None, 
        description="Test de prédiction réussi"
    )
    test_probability: Optional[float] = Field(
        None, 
        description="Probabilité du test"
    )
    test_error: Optional[str] = Field(
        None, 
        description="Erreur du test si échec"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "threshold_loaded": True,
                "preprocessor_ready": True,
                "timestamp": "2024-01-15T14:30:00",
                "test_prediction_success": True,
                "test_probability": 0.6543
            }
        }

class ModelInfoResponse(BaseModel):
    """Modèle pour les informations du modèle"""
    
    model_status: str = Field(..., description="Status du modèle")
    model_type: str = Field(..., description="Type de modèle")
    optimal_threshold: float = Field(..., description="Seuil optimal utilisé")
    features_count: int = Field(..., description="Nombre de features")
    last_loaded: str = Field(..., description="Dernière date de chargement")
    
    # Métriques du modèle (si disponibles)
    model_metrics: Optional[Dict[str, Any]] = Field(
        None, 
        description="Métriques de performance"
    )
    hyperparameters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Hyperparamètres du modèle"
    )
    preprocessing_info: Optional[Dict[str, Any]] = Field(
        None, 
        description="Informations sur le preprocessing"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "model_status": "loaded",
                "model_type": "XGBoost Champion",
                "optimal_threshold": 0.3510,
                "features_count": 11,
                "last_loaded": "2024-01-15T14:30:00",
                "model_metrics": {
                    "recall": 0.885,
                    "precision": 0.457,
                    "business_score": 0.0880
                }
            }
        }

class FakeClientResponse(BaseModel):
    """Modèle pour la réponse de génération de client fictif"""
    
    client_data: ClientInputAPI = Field(
        ..., 
        description="Données du client généré"
    )
    profile_type: str = Field(
        ..., 
        description="Type de profil généré"
    )
    generation_timestamp: str = Field(
        ..., 
        description="Horodatage de la génération"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "client_data": {
                    "contract": "Month-to-month",
                    "tenure": 3,
                    "monthly_charges": 85.0,
                    "total_charges": 255.0,
                    "payment_method": "Electronic check",
                    "internet_service": "Fiber optic",
                    "paperless_billing": "Yes",
                    "client_id": "fake_client_001"
                },
                "profile_type": "high_risk",
                "generation_timestamp": "2024-01-15T14:30:00"
            }
        }

class ErrorResponse(BaseModel):
    """Modèle pour les réponses d'erreur"""
    
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur détaillé")
    timestamp: str = Field(..., description="Horodatage de l'erreur")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "monthly_charges doit être > 0, reçu: -10.5",
                "timestamp": "2024-01-15T14:30:00"
            }
        }