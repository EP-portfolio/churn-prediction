"""
API FastAPI pour la prédiction de churn client
"""
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Imports locaux
from api.models import (
    ClientInputAPI,
    PredictionResponse, 
    HealthResponse,
    ModelInfoResponse,
    FakeClientResponse,
    ErrorResponse
)
from api.fake_data import generate_fake_client, get_available_profile_types, get_profile_description
from src.model_wrapper import ChurnPredictor

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================================
# INITIALISATION DE L'APPLICATION FASTAPI
# =====================================================

app = FastAPI(
    title="🎯 Churn Prediction API",
    description="""
    **API de prédiction de churn client pour télécommunications**
    
    Cette API utilise un modèle XGBoost optimisé pour prédire le risque de churn
    des clients télécoms avec 11 features et un seuil business optimal.
    
    ## Fonctionnalités principales :
    - **Prédiction client unique** avec recommandations business
    - **Génération de clients fictifs** pour démonstration
    - **Health checks** et monitoring
    - **Métadonnées modèle** pour transparence
    
    ## Modèle utilisé :
    - **Type** : XGBoost Champion 11 Features
    - **Recall** : 88.5% (objectif >80% ✅)
    - **Seuil optimal** : 35.10%
    - **Business Score** : Optimisé pour coûts acquisition/rétention
    """,
    version="1.0.0",
    contact={
        "name": "EP-Portfolio",
        "email": "m.eddyponton@gmail.com"
    },
    license_info={
        "name": "MIT License"
    }
)

# =====================================================
# CONFIGURATION CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# INITIALISATION DU PRÉDICTEUR
# =====================================================

predictor = None

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'API"""
    global predictor
    try:
        logger.info("🚀 Démarrage de l'API Churn Prediction...")
        predictor = ChurnPredictor()
        logger.info("✅ Prédicteur chargé avec succès")
        
        # Test de fonctionnement
        health = predictor.health_check()
        if health["status"] != "healthy":
            logger.warning(f"⚠️ Prédicteur en état dégradé: {health}")
        else:
            logger.info("✅ Health check initial: OK")
            
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}")
        traceback.print_exc()
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    logger.info("🛑 Arrêt de l'API Churn Prediction")

# =====================================================
# GESTIONNAIRE D'ERREURS GLOBAL
# =====================================================

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Gestionnaire pour les erreurs de validation Pydantic"""
    logger.error(f"Erreur de validation: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message=f"Données invalides: {str(exc)}",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Gestionnaire pour les erreurs générales"""
    logger.error(f"Erreur serveur: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError", 
            message="Erreur interne du serveur",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# =====================================================
# ENDPOINTS PRINCIPAUX
# =====================================================

@app.get("/", tags=["Root"])
async def root():
    """Endpoint racine avec informations générales"""
    return {
        "service": "Churn Prediction API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
        "model_info": "/model/info"
    }

@app.post(
    "/predict/client",
    response_model=PredictionResponse,
    tags=["Prediction"],
    summary="Prédiction de churn pour un client",
    description="""
    **Effectue une prédiction de churn pour un client unique.**
    
    L'API prend en entrée les 7 caractéristiques business du client et retourne :
    - Probabilité de churn [0-1]
    - Prédiction binaire (0=stable, 1=churn)  
    - Niveau de risque interprété
    - Recommandation d'action business
    - Score de confiance
    
    Le modèle calcule automatiquement les features engineered nécessaires.
    """
)
async def predict_client_churn(client_data: ClientInputAPI):
    """
    Prédiction de churn pour un client unique
    
    Args:
        client_data: Données du client (7 features)
        
    Returns:
        PredictionResponse: Résultat complet de la prédiction
        
    Raises:
        HTTPException: Si erreur dans la prédiction
    """
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prédicteur non initialisé"
        )
    
    try:
        logger.info(f"🔄 Prédiction pour client {client_data.client_id or 'anonyme'}")
        
        # Conversion en dict pour le prédicteur
        input_dict = {
            "contract": client_data.contract,
            "tenure": client_data.tenure, 
            "monthly_charges": client_data.monthly_charges,
            "total_charges": client_data.total_charges,
            "payment_method": client_data.payment_method,
            "internet_service": client_data.internet_service,
            "paperless_billing": client_data.paperless_billing
        }
        
        # Prédiction
        result = predictor.predict_single(input_dict, client_data.client_id)
        
        # Conversion en réponse API
        response = PredictionResponse(
            churn_probability=result.churn_probability,
            churn_prediction=result.churn_prediction,
            risk_level=result.risk_level,
            business_recommendation=result.business_recommendation,
            confidence_score=result.confidence_score,
            client_id=result.client_id,
            prediction_timestamp=result.prediction_timestamp,
            model_metadata=result.model_metadata
        )
        
        logger.info(f"✅ Prédiction terminée: P={result.churn_probability:.4f}, Risk={result.risk_level}")
        return response
        
    except ValueError as e:
        logger.error(f"❌ Erreur de validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Erreur prédiction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Monitoring"],
    summary="Health check du service",
    description="Vérifie l'état de santé du service et du modèle de prédiction"
)
async def health_check():
    """
    Health check du service
    
    Returns:
        HealthResponse: État de santé complet
    """
    if predictor is None:
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            threshold_loaded=False,
            preprocessor_ready=False,
            timestamp=datetime.now().isoformat(),
            test_prediction_success=False,
            test_error="Prédicteur non initialisé"
        )
    
    try:
        health_data = predictor.health_check()
        
        response = HealthResponse(
            status=health_data["status"],
            model_loaded=health_data["model_loaded"],
            threshold_loaded=health_data["threshold_loaded"], 
            preprocessor_ready=health_data["preprocessor_ready"],
            timestamp=health_data["timestamp"],
            test_prediction_success=health_data.get("test_prediction_success"),
            test_probability=health_data.get("test_probability"),
            test_error=health_data.get("test_error")
        )
        
        logger.info(f"Health check: {health_data['status']}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur health check: {e}")
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            threshold_loaded=False,
            preprocessor_ready=False,
            timestamp=datetime.now().isoformat(),
            test_prediction_success=False,
            test_error=str(e)
        )

@app.get(
    "/model/info",
    response_model=ModelInfoResponse,
    tags=["Monitoring"],
    summary="Informations sur le modèle",
    description="Retourne les métadonnées complètes du modèle de prédiction"
)
async def get_model_info():
    """
    Informations sur le modèle chargé
    
    Returns:
        ModelInfoResponse: Métadonnées complètes du modèle
    """
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prédicteur non initialisé"
        )
    
    try:
        model_info = predictor.get_model_info()
        
        response = ModelInfoResponse(
            model_status=model_info["model_status"],
            model_type=model_info.get("model_type", "Unknown"),
            optimal_threshold=model_info["optimal_threshold"],
            features_count=model_info["features_count"],
            last_loaded=model_info["last_loaded"],
            model_metrics=model_info.get("model_metrics"),
            hyperparameters=model_info.get("hyperparameters"),
            preprocessing_info=model_info.get("preprocessing_info")
        )
        
        logger.info("Informations modèle retournées")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération infos modèle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération infos: {str(e)}"
        )

@app.get(
    "/generate/fake-client",
    response_model=FakeClientResponse,
    tags=["Demo"],
    summary="Génération de client fictif",
    description="""
    **Génère un client fictif avec Faker pour démonstration.**
    
    Types de profils disponibles :
    - **random** : Profil complètement aléatoire
    - **high_risk** : Client à haut risque de churn
    - **stable** : Client fidèle et stable  
    - **new** : Nouveau client (0-3 mois)
    - **premium** : Client premium (services haut de gamme)
    
    Utile pour tester l'API et faire des démonstrations.
    """
)
async def generate_fake_client_endpoint(
    profile_type: str = Query(
        default="random",
        description="Type de profil à générer",
        enum=["random", "high_risk", "stable", "new", "premium"]
    )
):
    """
    Génère un client fictif pour démonstration
    
    Args:
        profile_type: Type de profil à générer
        
    Returns:
        FakeClientResponse: Client généré avec métadonnées
    """
    try:
        logger.info(f"🎭 Génération client fictif: {profile_type}")
        
        # Génération du client fictif
        fake_client_data = generate_fake_client(profile_type)
        
        # Conversion en modèle API
        client_input = ClientInputAPI(**fake_client_data)
        
        response = FakeClientResponse(
            client_data=client_input,
            profile_type=profile_type,
            generation_timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Client fictif généré: {profile_type}")
        return response
        
    except ValueError as e:
        logger.error(f"❌ Type de profil invalide: {e}")
        available_types = get_available_profile_types()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de profil invalide. Types disponibles: {available_types}"
        )
    except Exception as e:
        logger.error(f"❌ Erreur génération client fictif: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur génération: {str(e)}"
        )

@app.get(
    "/generate/profile-types",
    tags=["Demo"],
    summary="Types de profils disponibles",
    description="Liste tous les types de profils clients fictifs disponibles avec descriptions"
)
async def get_profile_types():
    """
    Liste des types de profils disponibles pour la génération
    
    Returns:
        Dict avec types et descriptions
    """
    try:
        profile_types = get_available_profile_types()
        
        profiles_info = {}
        for profile_type in profile_types:
            profiles_info[profile_type] = get_profile_description(profile_type)
        
        return {
            "available_profiles": profile_types,
            "descriptions": profiles_info,
            "usage": "Utilisez /generate/fake-client?profile_type=TYPE"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération types profils: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =====================================================
# ENDPOINT DE DÉMONSTRATION COMPLÈTE
# =====================================================

@app.get(
    "/demo/predict-fake-client",
    response_model=Dict[str, Any],
    tags=["Demo"],
    summary="Démonstration complète : génération + prédiction",
    description="Génère un client fictif ET fait la prédiction en une seule requête"
)
async def demo_predict_fake_client(
    profile_type: str = Query(
        default="random",
        description="Type de profil à générer et prédire",
        enum=["random", "high_risk", "stable", "new", "premium"]
    )
):
    """
    Démonstration complète : génère un client fictif et fait la prédiction
    
    Args:
        profile_type: Type de profil à générer
        
    Returns:
        Dict avec client généré + prédiction
    """
    try:
        logger.info(f"🎭🎯 Démo complète pour profil: {profile_type}")
        
        # 1. Génération client fictif
        fake_client_data = generate_fake_client(profile_type)
        client_input = ClientInputAPI(**fake_client_data)
        
        # 2. Prédiction sur ce client
        input_dict = {
            "contract": client_input.contract,
            "tenure": client_input.tenure,
            "monthly_charges": client_input.monthly_charges,
            "total_charges": client_input.total_charges,
            "payment_method": client_input.payment_method,
            "internet_service": client_input.internet_service,
            "paperless_billing": client_input.paperless_billing
        }
        
        prediction_result = predictor.predict_single(input_dict, client_input.client_id)
        
        # 3. Réponse combinée
        demo_result = {
            "demo_info": {
                "profile_type": profile_type,
                "description": get_profile_description(profile_type),
                "timestamp": datetime.now().isoformat()
            },
            "generated_client": client_input.dict(),
            "prediction": {
                "churn_probability": prediction_result.churn_probability,
                "churn_prediction": prediction_result.churn_prediction,
                "risk_level": prediction_result.risk_level,
                "business_recommendation": prediction_result.business_recommendation,
                "confidence_score": prediction_result.confidence_score
            },
            "analysis": {
                "profile_matches_prediction": (
                    "high_risk" in profile_type and prediction_result.churn_prediction == 1
                ) or (
                    "stable" in profile_type and prediction_result.churn_prediction == 0
                ),
                "threshold_used": predictor.optimal_threshold
            }
        }
        
        logger.info(f"✅ Démo terminée: {profile_type} → P={prediction_result.churn_probability:.4f}")
        return demo_result
        
    except Exception as e:
        logger.error(f"❌ Erreur démo complète: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur démo: {str(e)}"
        )

# =====================================================
# MAIN POUR EXÉCUTION DIRECTE
# =====================================================

if __name__ == "__main__":
    import uvicorn
    
    # Configuration pour développement
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )