"""
Wrapper du modèle de prédiction de churn
"""
import joblib
import json
import logging
import numpy as np
from typing import Dict, Union, Any, Tuple, List
from pathlib import Path
from datetime import datetime

from src.preprocessing import ChurnPreprocessor
from config.settings import MODEL_PATH, THRESHOLD_PATH, HYPERPARAMS_PATH, METRICS_PATH

logger = logging.getLogger(__name__)

class ChurnPredictionResult:
    """Classe pour structurer les résultats de prédiction"""
    
    def __init__(self, client_id: str = None):
        self.client_id = client_id
        self.churn_probability: float = 0.0
        self.churn_prediction: int = 0
        self.risk_level: str = ""
        self.business_recommendation: str = ""
        self.confidence_score: float = 0.0
        self.prediction_timestamp: str = datetime.now().isoformat()
        self.model_metadata: Dict[str, Any] = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le résultat en dictionnaire"""
        return {
            'client_id': self.client_id,
            'churn_probability': round(self.churn_probability, 4),
            'churn_prediction': self.churn_prediction,
            'risk_level': self.risk_level,
            'business_recommendation': self.business_recommendation,
            'confidence_score': round(self.confidence_score, 4),
            'prediction_timestamp': self.prediction_timestamp,
            'model_metadata': self.model_metadata
        }

class ChurnPredictor:
    """Wrapper principal pour la prédiction de churn"""
    
    def __init__(self):
        """Initialise le prédicteur avec modèle + seuil + preprocessor"""
        self.model = None
        self.optimal_threshold = None
        self.hyperparams = None
        self.metrics = None
        self.preprocessor = None
        self.is_loaded = False
        
        # Chargement automatique
        self._load_model_artifacts()
        self._initialize_preprocessor()
        
        logger.info("✅ ChurnPredictor initialisé avec succès")
    
    def _load_model_artifacts(self) -> None:
        """Charge tous les artefacts du modèle"""
        try:
            # 1. Modèle champion
            logger.info(f"Chargement modèle depuis: {MODEL_PATH}")
            self.model = joblib.load(MODEL_PATH)
            
            # 2. Seuil optimal
            logger.info(f"Chargement seuil depuis: {THRESHOLD_PATH}")
            self.optimal_threshold = joblib.load(THRESHOLD_PATH)
            
            # 3. Hyperparamètres (optionnel)
            if HYPERPARAMS_PATH.exists():
                with open(HYPERPARAMS_PATH, 'r') as f:
                    self.hyperparams = json.load(f)
                logger.info("✅ Hyperparamètres chargés")
            
            # 4. Métriques (optionnel)
            if METRICS_PATH.exists():
                with open(METRICS_PATH, 'r') as f:
                    self.metrics = json.load(f)
                logger.info("✅ Métriques chargées")
            
            self.is_loaded = True
            logger.info(f"✅ Modèle champion chargé, seuil optimal: {self.optimal_threshold:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            raise RuntimeError(f"Impossible de charger le modèle: {e}")
    
    def _initialize_preprocessor(self) -> None:
        """Initialise le preprocessor"""
        try:
            self.preprocessor = ChurnPreprocessor()
            logger.info("✅ Preprocessor initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation preprocessor: {e}")
            raise RuntimeError(f"Impossible d'initialiser le preprocessor: {e}")
    
    def _interpret_probability(self, probability: float) -> Tuple[str, str]:
        """
        Interprète la probabilité en niveau de risque et recommandation business
        
        Args:
            probability: Probabilité de churn [0-1]
            
        Returns:
            Tuple[str, str]: (risk_level, business_recommendation)
        """
        if probability >= self.optimal_threshold:
            if probability >= 0.8:
                return "Critical Risk", "🚨 ACTION IMMÉDIATE: Contact urgent + offre de rétention premium"
            elif probability >= 0.65:
                return "High Risk", "⚠️ PRIORITÉ ÉLEVÉE: Contact sous 48h + analyse besoins client"
            else:
                return "Medium-High Risk", "📞 SURVEILLANCE: Contact sous 1 semaine + suivi personnalisé"
        else:
            if probability >= 0.4:
                return "Medium Risk", "👀 MONITORING: Surveillance renforcée + enquête satisfaction"
            elif probability >= 0.2:
                return "Low-Medium Risk", "📊 TRACKING: Suivi mensuel + programme fidélité"
            else:
                return "Low Risk", "✅ STABLE: Client fidèle - maintenir qualité service"
    
    def _calculate_confidence(self, probability: float) -> float:
        """
        Calcule un score de confiance basé sur la distance au seuil
        
        Args:
            probability: Probabilité de churn
            
        Returns:
            float: Score de confiance [0-1]
        """
        # Distance au seuil optimal (plus on est loin, plus on est confiant)
        distance_to_threshold = abs(probability - self.optimal_threshold)
        
        # Normaliser par la distance maximale possible
        max_distance = max(self.optimal_threshold, 1 - self.optimal_threshold)
        
        # Score de confiance (0.5 minimum, 1.0 maximum)
        confidence = 0.5 + (distance_to_threshold / max_distance) * 0.5
        
        return min(confidence, 1.0)
    
    def predict_single(self, client_data: Dict[str, Union[str, int, float]], 
                      client_id: str = None) -> ChurnPredictionResult:
        """
        Prédiction pour un client unique
        
        Args:
            client_data: Données du client (7 features d'input)
            client_id: Identifiant optionnel du client
            
        Returns:
            ChurnPredictionResult: Résultat structuré de la prédiction
            
        Raises:
            RuntimeError: Si le modèle n'est pas chargé
            ValueError: Si erreur dans les données
        """
        if not self.is_loaded:
            raise RuntimeError("Modèle non chargé")
        
        logger.info(f"🔄 Prédiction pour client {client_id or 'anonyme'}")
        
        try:
            # 1. Preprocessing
            feature_vector, preprocessing_metadata = self.preprocessor.preprocess(client_data)
            
            # 2. Prédiction du modèle
            probability_array = self.model.predict_proba(feature_vector.reshape(1, -1))
            churn_probability = probability_array[0, 1]  # Probabilité classe 1 (churn)
            
            # 3. Décision binaire avec seuil optimal
            churn_prediction = 1 if churn_probability >= self.optimal_threshold else 0
            
            # 4. Interprétation business
            risk_level, business_recommendation = self._interpret_probability(churn_probability)
            
            # 5. Score de confiance
            confidence_score = self._calculate_confidence(churn_probability)
            
            # 6. Construction du résultat
            result = ChurnPredictionResult(client_id)
            result.churn_probability = float(churn_probability)
            result.churn_prediction = int(churn_prediction)
            result.risk_level = risk_level
            result.business_recommendation = business_recommendation
            result.confidence_score = float(confidence_score)
            result.model_metadata = {
                'optimal_threshold': float(self.optimal_threshold),
                'preprocessing_metadata': preprocessing_metadata,
                'model_version': 'XGBoost_Champion_11_Features',
                'features_used': preprocessing_metadata['feature_names']
            }
            
            logger.info(f"✅ Prédiction terminée: P(churn)={churn_probability:.4f}, "
                       f"Decision={churn_prediction}, Risk={risk_level}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction: {e}")
            raise ValueError(f"Erreur lors de la prédiction: {e}")
    
    def predict_batch(self, clients_data: List[Dict[str, Union[str, int, float]]], 
                     client_ids: List[str] = None) -> List[ChurnPredictionResult]:
        """
        Prédiction par lot pour plusieurs clients
        
        Args:
            clients_data: Liste des données clients
            client_ids: Liste optionnelle des identifiants
            
        Returns:
            List[ChurnPredictionResult]: Liste des résultats
        """
        if not self.is_loaded:
            raise RuntimeError("Modèle non chargé")
        
        logger.info(f"🔄 Prédiction batch pour {len(clients_data)} clients")
        
        if client_ids is None:
            client_ids = [f"client_{i}" for i in range(len(clients_data))]
        
        if len(client_ids) != len(clients_data):
            raise ValueError("Nombre de client_ids différent du nombre de clients")
        
        results = []
        for i, (client_data, client_id) in enumerate(zip(clients_data, client_ids)):
            try:
                result = self.predict_single(client_data, client_id)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Erreur client {i} ({client_id}): {e}")
                # Créer un résultat d'erreur
                error_result = ChurnPredictionResult(client_id)
                error_result.risk_level = "Error"
                error_result.business_recommendation = f"Erreur: {str(e)}"
                results.append(error_result)
        
        logger.info(f"✅ Prédiction batch terminée: {len(results)} résultats")
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle chargé
        
        Returns:
            Dict avec métadonnées complètes
        """
        if not self.is_loaded:
            return {"status": "Model not loaded"}
        
        info = {
            "model_status": "loaded",
            "model_type": "XGBoost Champion",
            "optimal_threshold": float(self.optimal_threshold),
            "features_count": 11,
            "last_loaded": datetime.now().isoformat()
        }
        
        # Ajouter métriques si disponibles
        if self.metrics:
            info["model_metrics"] = self.metrics
        
        # Ajouter hyperparamètres si disponibles
        if self.hyperparams:
            info["hyperparameters"] = self.hyperparams
        
        # Ajouter infos preprocessor
        if self.preprocessor:
            info["preprocessing_info"] = self.preprocessor.get_feature_info()
        
        return info
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé du modèle
        
        Returns:
            Dict avec status de santé
        """
        health = {
            "status": "healthy" if self.is_loaded else "unhealthy",
            "model_loaded": self.is_loaded,
            "threshold_loaded": self.optimal_threshold is not None,
            "preprocessor_ready": self.preprocessor is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Test rapide si tout est chargé
        if self.is_loaded:
            try:
                # Test avec données factices
                test_data = {
                    'contract': 'Month-to-month',
                    'tenure': 12,
                    'monthly_charges': 75.0,
                    'total_charges': 900.0,
                    'payment_method': 'Electronic check',
                    'internet_service': 'Fiber optic',
                    'paperless_billing': 'Yes'
                }
                
                test_result = self.predict_single(test_data, "health_check")
                health["test_prediction_success"] = True
                health["test_probability"] = test_result.churn_probability
                
            except Exception as e:
                health["status"] = "degraded"
                health["test_prediction_success"] = False
                health["test_error"] = str(e)
        
        return health