"""
Pipeline de preprocessing complet pour la prédiction de churn
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Union, Any, Tuple
from pydantic import BaseModel, Field, validator
from src.encoders import EncoderManager
from src.feature_engineering import compute_all_engineered_features, validate_engineered_features
from config.settings import (
    MODEL_FEATURES, 
    CONTRACT_VALUES, 
    PAYMENT_METHOD_VALUES,
    INTERNET_SERVICE_VALUES,
    PAPERLESS_BILLING_VALUES,
    MIN_TENURE,
    MIN_MONTHLY_CHARGES,
    MIN_TOTAL_CHARGES
)

logger = logging.getLogger(__name__)

class ClientInput(BaseModel):
    """Modèle Pydantic pour validation des inputs utilisateur"""
    
    contract: str = Field(..., description="Type de contrat")
    tenure: int = Field(..., ge=MIN_TENURE, description="Ancienneté en mois")
    monthly_charges: float = Field(..., gt=MIN_MONTHLY_CHARGES, description="Facturation mensuelle")
    total_charges: float = Field(..., ge=MIN_TOTAL_CHARGES, description="Total facturé")
    payment_method: str = Field(..., description="Mode de paiement")
    internet_service: str = Field(..., description="Service Internet")
    paperless_billing: str = Field(..., description="Facturation numérique")
    
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

class ChurnPreprocessor:
    """Pipeline de preprocessing pour la prédiction de churn"""
    
    def __init__(self):
        """Initialise le preprocessor avec les encoders"""
        self.encoder_manager = EncoderManager()
        self.feature_order = MODEL_FEATURES.copy()
        logger.info(f"✅ ChurnPreprocessor initialisé avec {len(self.feature_order)} features")
        logger.debug(f"Ordre des features: {self.feature_order}")
    
    def validate_input(self, client_data: Dict[str, Union[str, int, float]]) -> ClientInput:
        """
        Valide les données d'entrée avec Pydantic
        
        Args:
            client_data: Dict avec les données brutes du client
            
        Returns:
            ClientInput: Objet validé
            
        Raises:
            ValueError: Si les données ne sont pas valides
        """
        try:
            validated_input = ClientInput(**client_data)
            logger.debug(f"✅ Input validé: {validated_input.dict()}")
            return validated_input
        except Exception as e:
            logger.error(f"❌ Validation input failed: {e}")
            raise ValueError(f"Données invalides: {e}")
    
    def encode_categorical_features(self, validated_input: ClientInput) -> Dict[str, int]:
        """
        Encode les features catégorielles
        
        Args:
            validated_input: Données validées
            
        Returns:
            Dict avec les features encodées
        """
        categorical_data = {
            'Contract': validated_input.contract,
            'PaymentMethod': validated_input.payment_method,
            'InternetService': validated_input.internet_service,
            'PaperlessBilling': validated_input.paperless_billing
        }
        
        logger.debug(f"Encodage des features catégorielles: {categorical_data}")
        encoded_features = self.encoder_manager.encode_all_features(categorical_data)
        logger.debug(f"✅ Features encodées: {encoded_features}")
        
        return encoded_features
    
    def compute_engineered_features(self, validated_input: ClientInput) -> Dict[str, Union[float, int]]:
        """
        Calcule les features engineered
        
        Args:
            validated_input: Données validées
            
        Returns:
            Dict avec les features calculées
        """
        logger.debug(f"Calcul features engineered pour tenure={validated_input.tenure}")
        
        engineered_features = compute_all_engineered_features(
            tenure=validated_input.tenure,
            monthly_charges=validated_input.monthly_charges,
            total_charges=validated_input.total_charges
        )
        
        # Validation des résultats
        if not validate_engineered_features(engineered_features):
            raise ValueError("Features engineered invalides")
        
        return engineered_features
    
    def build_feature_vector(self, validated_input: ClientInput, encoded_features: Dict[str, int], 
                           engineered_features: Dict[str, Union[float, int]]) -> np.ndarray:
        """
        Construit le vecteur de features dans l'ordre exact du modèle
        
        Args:
            validated_input: Données validées
            encoded_features: Features catégorielles encodées
            engineered_features: Features calculées
            
        Returns:
            np.ndarray: Vecteur de features ordonné pour le modèle
        """
        # Construire dict complet de toutes les features
        all_features = {
            # Features brutes
            'tenure': validated_input.tenure,
            'MonthlyCharges': validated_input.monthly_charges,
            'TotalCharges': validated_input.total_charges,
            
            # Features encodées
            **encoded_features,
            
            # Features engineered
            **engineered_features
        }
        
        logger.debug(f"Features complètes: {all_features}")
        
        # Construire le vecteur dans l'ordre exact du modèle
        feature_vector = []
        for feature_name in self.feature_order:
            if feature_name not in all_features:
                raise ValueError(f"Feature manquante: {feature_name}")
            
            feature_vector.append(all_features[feature_name])
        
        # Convertir en numpy array
        feature_array = np.array(feature_vector, dtype=np.float64)
        
        logger.info(f"✅ Vecteur de features construit: shape={feature_array.shape}")
        logger.debug(f"Feature vector: {feature_array}")
        
        return feature_array
    
    def preprocess(self, client_data: Dict[str, Union[str, int, float]]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Pipeline complet de preprocessing
        
        Args:
            client_data: Données brutes du client
            
        Returns:
            Tuple[np.ndarray, Dict]: (feature_vector, metadata)
            
        Raises:
            ValueError: Si erreur dans le pipeline
        """
        logger.info(f"🔄 Début preprocessing pour: {client_data}")
        
        try:
            # 1. Validation des inputs
            validated_input = self.validate_input(client_data)
            
            # 2. Encodage des features catégorielles
            encoded_features = self.encode_categorical_features(validated_input)
            
            # 3. Calcul des features engineered
            engineered_features = self.compute_engineered_features(validated_input)
            
            # 4. Construction du vecteur final
            feature_vector = self.build_feature_vector(validated_input, encoded_features, engineered_features)
            
            # 5. Métadonnées pour debugging/logging
            metadata = {
                'input_data': validated_input.dict(),
                'encoded_features': encoded_features,
                'engineered_features': engineered_features,
                'feature_names': self.feature_order,
                'feature_vector_shape': feature_vector.shape
            }
            
            logger.info(f"✅ Preprocessing terminé avec succès")
            return feature_vector, metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur preprocessing: {e}")
            raise
    
    def preprocess_batch(self, clients_data: List[Dict[str, Union[str, int, float]]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Preprocessing par lot pour plusieurs clients
        
        Args:
            clients_data: Liste des données clients
            
        Returns:
            Tuple[np.ndarray, List[Dict]]: (feature_matrix, metadatas)
        """
        logger.info(f"🔄 Preprocessing batch de {len(clients_data)} clients")
        
        feature_vectors = []
        metadatas = []
        
        for i, client_data in enumerate(clients_data):
            try:
                feature_vector, metadata = self.preprocess(client_data)
                feature_vectors.append(feature_vector)
                metadatas.append(metadata)
            except Exception as e:
                logger.error(f"❌ Erreur client {i}: {e}")
                raise ValueError(f"Erreur preprocessing client {i}: {e}")
        
        # Convertir en matrice numpy
        feature_matrix = np.array(feature_vectors)
        
        logger.info(f"✅ Preprocessing batch terminé: shape={feature_matrix.shape}")
        return feature_matrix, metadatas
    
    def get_feature_info(self) -> Dict[str, Any]:
        """Retourne les informations sur les features et encoders"""
        return {
            'model_features': self.feature_order,
            'categorical_features_info': self.encoder_manager.get_all_features_info(),
            'input_constraints': {
                'tenure': f'>= {MIN_TENURE}',
                'monthly_charges': f'> {MIN_MONTHLY_CHARGES}',
                'total_charges': f'>= {MIN_TOTAL_CHARGES}'
            }
        }