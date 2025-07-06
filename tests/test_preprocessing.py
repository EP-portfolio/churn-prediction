"""
Tests de validation du pipeline de preprocessing (version sans pytest)
"""
import numpy as np
import sys
from pathlib import Path

# Ajouter le dossier parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from src.preprocessing import ChurnPreprocessor, ClientInput
from src.feature_engineering import (
    calculate_ratio_monthly_charges_tenure,
    calculate_ratio_total_monthly_tenure,
    calculate_tenure_segment_encoded,
    calculate_is_new_customer,
    compute_all_engineered_features
)
from src.encoders import EncoderManager

def test_feature_engineering():
    """Tests des fonctions de feature engineering"""
    print("🧪 Test Feature Engineering...")
    
    # Test ratio monthly charges tenure
    assert calculate_ratio_monthly_charges_tenure(50.0, 12) == 50.0 / 13
    assert calculate_ratio_monthly_charges_tenure(75.5, 0) == 75.5 / 1
    print("✅ Ratio MonthlyCharges/tenure OK")
    
    # Test ratio total
    assert calculate_ratio_total_monthly_tenure(600.0, 50.0, 12) == 600.0 / (50.0 * 12)
    assert calculate_ratio_total_monthly_tenure(0.0, 50.0, 0) == 1.0  # Cas spécial
    print("✅ Ratio TotalCharges/(MonthlyCharges*tenure) OK")
    
    # Test tenure segments
    assert calculate_tenure_segment_encoded(0) == 0   # Nouveaux
    assert calculate_tenure_segment_encoded(7) == 1   # Junior
    assert calculate_tenure_segment_encoded(13) == 2  # Moyen
    assert calculate_tenure_segment_encoded(25) == 3  # Senior
    print("✅ Tenure segments OK")
    
    # Test nouveau client
    assert calculate_is_new_customer(0) == 1
    assert calculate_is_new_customer(6) == 1
    assert calculate_is_new_customer(7) == 0
    print("✅ Is new customer OK")

def test_encoders():
    """Tests du gestionnaire d'encoders"""
    print("🧪 Test Encoders...")
    
    encoder_manager = EncoderManager()
    
    # Test Contract
    assert encoder_manager.encode_feature('Contract', 'Month-to-month') == 0
    assert encoder_manager.encode_feature('Contract', 'One year') == 1
    assert encoder_manager.encode_feature('Contract', 'Two year') == 2
    print("✅ Contract encoding OK")
    
    # Test PaymentMethod
    assert encoder_manager.encode_feature('PaymentMethod', 'Bank transfer (automatic)') == 0
    assert encoder_manager.encode_feature('PaymentMethod', 'Electronic check') == 2
    print("✅ PaymentMethod encoding OK")

def test_preprocessing_pipeline():
    """Test du pipeline complet"""
    print("🧪 Test Pipeline Complet...")
    
    preprocessor = ChurnPreprocessor()
    
    # Cas test normal
    client_data = {
        'contract': 'Month-to-month',
        'tenure': 12,
        'monthly_charges': 75.50,
        'total_charges': 906.00,
        'payment_method': 'Electronic check',
        'internet_service': 'Fiber optic',
        'paperless_billing': 'Yes'
    }
    
    feature_vector, metadata = preprocessor.preprocess(client_data)
    
    assert isinstance(feature_vector, np.ndarray)
    assert len(feature_vector) == 11
    assert feature_vector.dtype == np.float64
    print("✅ Pipeline normal OK")
    
    # Cas nouveau client
    nouveau_client = {
        'contract': 'Month-to-month',
        'tenure': 0,
        'monthly_charges': 50.00,
        'total_charges': 0.00,
        'payment_method': 'Electronic check',
        'internet_service': 'Fiber optic',
        'paperless_billing': 'Yes'
    }
    
    feature_vector_new, metadata_new = preprocessor.preprocess(nouveau_client)
    assert metadata_new['engineered_features']['is_new_customer'] == 1
    assert metadata_new['engineered_features']['Ratio_TotalCharges_MonthlyCharges*tenure'] == 1.0
    print("✅ Pipeline nouveau client OK")

if __name__ == "__main__":
    print("🧪 VALIDATION DU PIPELINE DE PREPROCESSING")
    print("=" * 50)
    
    try:
        test_feature_engineering()
        test_encoders()
        test_preprocessing_pipeline()
        
        print("\n🎉 TOUS LES TESTS PASSÉS AVEC SUCCÈS !")
        print("📋 Le pipeline de preprocessing est prêt pour la Phase 2 (API FastAPI)")
        
    except Exception as e:
        print(f"\n❌ ERREUR DANS LES TESTS: {e}")
        raise