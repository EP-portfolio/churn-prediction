"""
Feature Engineering - Calcul des features dérivées
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Union, Any
from config.settings import TENURE_BINS, TENURE_LABELS, TENURE_SEGMENT_MAPPING

logger = logging.getLogger(__name__)

def calculate_ratio_monthly_charges_tenure(monthly_charges: float, tenure: int) -> float:
    """
    Calcule le ratio MonthlyCharges / (tenure + 1)
    
    Args:
        monthly_charges: Facturation mensuelle (> 0)
        tenure: Ancienneté en mois (>= 0)
        
    Returns:
        float: Ratio calculé
    """
    if monthly_charges <= 0:
        raise ValueError(f"MonthlyCharges doit être > 0, reçu: {monthly_charges}")
    
    if tenure < 0:
        raise ValueError(f"Tenure doit être >= 0, reçu: {tenure}")
    
    ratio = monthly_charges / (tenure + 1)
    logger.debug(f"Ratio MonthlyCharges/tenure: {monthly_charges}/{tenure+1} = {ratio:.4f}")
    
    return ratio

def calculate_ratio_total_monthly_tenure(total_charges: float, monthly_charges: float, tenure: int) -> float:
    """
    Calcule le ratio TotalCharges / (MonthlyCharges * tenure)
    Gestion spéciale : si tenure = 0, retourne 1 (comme fillna(1) du notebook)
    
    Args:
        total_charges: Total facturé (>= 0)
        monthly_charges: Facturation mensuelle (> 0)  
        tenure: Ancienneté en mois (>= 0)
        
    Returns:
        float: Ratio calculé
    """
    if total_charges < 0:
        raise ValueError(f"TotalCharges doit être >= 0, reçu: {total_charges}")
    
    if monthly_charges <= 0:
        raise ValueError(f"MonthlyCharges doit être > 0, reçu: {monthly_charges}")
    
    if tenure < 0:
        raise ValueError(f"Tenure doit être >= 0, reçu: {tenure}")
    
    # Cas spécial : nouveau client (tenure = 0) → ratio = 1
    if tenure == 0:
        logger.debug(f"Tenure = 0, ratio forcé à 1 (nouveau client)")
        return 1.0
    
    # Calcul normal
    denominator = monthly_charges * tenure
    ratio = total_charges / denominator
    
    logger.debug(f"Ratio TotalCharges/(MonthlyCharges*tenure): {total_charges}/({monthly_charges}*{tenure}) = {ratio:.4f}")
    
    return ratio

def calculate_tenure_segment_encoded(tenure: int) -> int:
    """
    Calcule le segment d'ancienneté encodé
    Reproduit exactement: pd.cut avec bins=[-1, 6, 12, 24, 100]
    
    Args:
        tenure: Ancienneté en mois (>= 0)
        
    Returns:
        int: Segment encodé (0, 1, 2, ou 3)
    """
    if tenure < 0:
        raise ValueError(f"Tenure doit être >= 0, reçu: {tenure}")
    
    # Reproduction exacte de la logique pd.cut du notebook
    if tenure <= 6:
        segment = 'Nouveaux_0-6m'
    elif tenure <= 12:
        segment = 'Junior_6-12m'
    elif tenure <= 24:
        segment = 'Moyen_12-24m'
    else:  # tenure > 24
        segment = 'Senior_24m+'
    
    # Encodage avec le mapping du notebook
    encoded_segment = TENURE_SEGMENT_MAPPING[segment]
    
    logger.debug(f"Tenure {tenure} mois → Segment '{segment}' → Encodé {encoded_segment}")
    
    return encoded_segment

def calculate_is_new_customer(tenure: int) -> int:
    """
    Détermine si le client est nouveau (tenure <= 6)
    Reproduit exactement: (tenure <= 6).astype(int)
    
    Args:
        tenure: Ancienneté en mois (>= 0)
        
    Returns:
        int: 1 si nouveau client, 0 sinon
    """
    if tenure < 0:
        raise ValueError(f"Tenure doit être >= 0, reçu: {tenure}")
    
    is_new = 1 if tenure <= 6 else 0
    
    logger.debug(f"Tenure {tenure} mois → Is new customer: {is_new}")
    
    return is_new

def compute_all_engineered_features(tenure: int, monthly_charges: float, total_charges: float) -> Dict[str, Union[float, int]]:
    """
    Calcule toutes les features engineered en une fois
    
    Args:
        tenure: Ancienneté en mois (>= 0)
        monthly_charges: Facturation mensuelle (> 0)
        total_charges: Total facturé (>= 0)
        
    Returns:
        Dict avec toutes les features calculées
        
    Raises:
        ValueError: Si les contraintes ne sont pas respectées
    """
    logger.info(f"Calcul features engineered pour: tenure={tenure}, monthly={monthly_charges}, total={total_charges}")
    
    try:
        # Validation globale des inputs
        if tenure < 0:
            raise ValueError(f"tenure doit être >= 0, reçu: {tenure}")
        if monthly_charges <= 0:
            raise ValueError(f"monthly_charges doit être > 0, reçu: {monthly_charges}")
        if total_charges < 0:
            raise ValueError(f"total_charges doit être >= 0, reçu: {total_charges}")
        
        # Calcul de toutes les features
        features = {
            'Ratio_MonthlyCharges_tenure': calculate_ratio_monthly_charges_tenure(monthly_charges, tenure),
            'tenure_segment_encoded': calculate_tenure_segment_encoded(tenure),
            'is_new_customer': calculate_is_new_customer(tenure),
            'Ratio_TotalCharges_MonthlyCharges*tenure': calculate_ratio_total_monthly_tenure(total_charges, monthly_charges, tenure)
        }
        
        logger.info(f"✅ Features engineered calculées: {features}")
        return features
        
    except Exception as e:
        logger.error(f"❌ Erreur calcul features engineered: {e}")
        raise

def validate_engineered_features(features: Dict[str, Union[float, int]]) -> bool:
    """
    Valide que les features calculées sont cohérentes
    
    Args:
        features: Dict avec les features calculées
        
    Returns:
        bool: True si tout est valide
    """
    required_features = [
        'Ratio_MonthlyCharges_tenure',
        'tenure_segment_encoded', 
        'is_new_customer',
        'Ratio_TotalCharges_MonthlyCharges*tenure'
    ]
    
    # Vérifier présence de toutes les features
    for feature in required_features:
        if feature not in features:
            logger.error(f"Feature manquante: {feature}")
            return False
    
    # Vérifier les types et ranges
    checks = [
        features['Ratio_MonthlyCharges_tenure'] > 0,  # Ratio positif
        features['tenure_segment_encoded'] in [0, 1, 2, 3],  # Segment valide
        features['is_new_customer'] in [0, 1],  # Booléen
        features['Ratio_TotalCharges_MonthlyCharges*tenure'] >= 0  # Ratio positif ou nul
    ]
    
    if not all(checks):
        logger.error(f"Validation failed pour les features: {features}")
        return False
    
    logger.debug("✅ Toutes les features engineered sont valides")
    return True