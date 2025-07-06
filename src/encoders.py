"""
Gestionnaire des encoders pour les features catégorielles
"""
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Union
from config.settings import ENCODER_FILES, CONTRACT_VALUES, PAYMENT_METHOD_VALUES, INTERNET_SERVICE_VALUES, PAPERLESS_BILLING_VALUES

logger = logging.getLogger(__name__)

class EncoderManager:
    """Gestionnaire centralisé des encoders Label"""
    
    def __init__(self):
        self.encoders = {}
        self.feature_mappings = {
            'Contract': CONTRACT_VALUES,
            'PaymentMethod': PAYMENT_METHOD_VALUES,
            'InternetService': INTERNET_SERVICE_VALUES,
            'PaperlessBilling': PAPERLESS_BILLING_VALUES
        }
        self._load_encoders()
    
    def _load_encoders(self) -> None:
        """Charge tous les encoders depuis les fichiers sauvegardés"""
        for feature_name, encoder_path in ENCODER_FILES.items():
            try:
                with open(encoder_path, 'rb') as f:
                    encoder = pickle.load(f)
                    self.encoders[feature_name] = encoder
                    logger.info(f"✅ Encoder {feature_name} chargé depuis {encoder_path}")
            except FileNotFoundError:
                logger.error(f"❌ Encoder {feature_name} non trouvé : {encoder_path}")
                raise FileNotFoundError(f"Encoder requis manquant : {encoder_path}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement encoder {feature_name}: {e}")
                raise
    
    def encode_feature(self, feature_name: str, value: str) -> int:
        """
        Encode une valeur catégorielle en entier
        
        Args:
            feature_name: Nom de la feature (Contract, PaymentMethod, etc.)
            value: Valeur à encoder
            
        Returns:
            int: Valeur encodée
            
        Raises:
            ValueError: Si la valeur n'est pas dans l'encoder
            KeyError: Si l'encoder n'existe pas
        """
        if feature_name not in self.encoders:
            raise KeyError(f"Encoder {feature_name} non disponible")
        
        # Validation que la valeur est autorisée
        if value not in self.feature_mappings[feature_name]:
            valid_values = self.feature_mappings[feature_name]
            raise ValueError(f"Valeur '{value}' invalide pour {feature_name}. "
                           f"Valeurs autorisées : {valid_values}")
        
        try:
            encoded_value = self.encoders[feature_name].transform([value])[0]
            logger.debug(f"Encodage {feature_name}: '{value}' → {encoded_value}")
            return int(encoded_value)
        except Exception as e:
            logger.error(f"Erreur encodage {feature_name}='{value}': {e}")
            raise ValueError(f"Impossible d'encoder {feature_name}='{value}'")
    
    def encode_all_features(self, data: Dict[str, str]) -> Dict[str, int]:
        """
        Encode toutes les features catégorielles d'un dictionnaire
        
        Args:
            data: Dict avec les valeurs non-encodées
            
        Returns:
            Dict avec les valeurs encodées
        """
        encoded_data = {}
        
        for feature_name in self.encoders.keys():
            if feature_name in data:
                encoded_data[feature_name] = self.encode_feature(feature_name, data[feature_name])
        
        return encoded_data
    
    def validate_input_values(self, data: Dict[str, str]) -> Dict[str, bool]:
        """
        Valide que toutes les valeurs d'input sont autorisées
        
        Args:
            data: Dict avec les valeurs à valider
            
        Returns:
            Dict avec résultats validation par feature
        """
        validation_results = {}
        
        for feature_name, allowed_values in self.feature_mappings.items():
            if feature_name in data:
                is_valid = data[feature_name] in allowed_values
                validation_results[feature_name] = is_valid
                
                if not is_valid:
                    logger.warning(f"Valeur invalide {feature_name}='{data[feature_name]}'. "
                                 f"Autorisées: {allowed_values}")
        
        return validation_results
    
    def get_feature_info(self, feature_name: str) -> Dict[str, Any]:
        """
        Retourne les informations d'une feature catégorielle
        
        Args:
            feature_name: Nom de la feature
            
        Returns:
            Dict avec valeurs autorisées et mapping
        """
        if feature_name not in self.encoders:
            raise KeyError(f"Feature {feature_name} non trouvée")
        
        encoder = self.encoders[feature_name]
        allowed_values = self.feature_mappings[feature_name]
        
        # Créer le mapping valeur → code
        mapping = {}
        for value in allowed_values:
            try:
                encoded = encoder.transform([value])[0]
                mapping[value] = int(encoded)
            except:
                mapping[value] = None
        
        return {
            'feature_name': feature_name,
            'allowed_values': allowed_values,
            'mapping': mapping,
            'encoder_classes': list(encoder.classes_)
        }
    
    def get_all_features_info(self) -> Dict[str, Dict[str, Any]]:
        """Retourne les infos de toutes les features"""
        return {name: self.get_feature_info(name) for name in self.encoders.keys()}