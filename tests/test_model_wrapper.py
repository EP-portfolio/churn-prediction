"""
Tests de validation du model wrapper
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from src.model_wrapper import ChurnPredictor, ChurnPredictionResult

def test_model_loading():
    """Test du chargement du modèle"""
    print("🧪 Test Model Loading...")
    
    predictor = ChurnPredictor()
    
    # Vérifications basiques
    assert predictor.is_loaded == True
    assert predictor.model is not None
    assert predictor.optimal_threshold is not None
    assert predictor.preprocessor is not None
    
    print(f"✅ Modèle chargé avec seuil: {predictor.optimal_threshold:.4f}")
    return predictor

def test_single_prediction(predictor):
    """Test de prédiction unique"""
    print("🧪 Test Single Prediction...")
    
    # Cas test client à risque
    client_risque = {
        'contract': 'Month-to-month',
        'tenure': 3,  # Nouveau client
        'monthly_charges': 85.0,  # Facture élevée
        'total_charges': 255.0,
        'payment_method': 'Electronic check',  # Mode de paiement risqué
        'internet_service': 'Fiber optic',
        'paperless_billing': 'Yes'
    }
    
    result = predictor.predict_single(client_risque, "test_client_001")
    
    # Vérifications
    assert isinstance(result, ChurnPredictionResult)
    assert 0 <= result.churn_probability <= 1
    assert result.churn_prediction in [0, 1]
    assert result.risk_level != ""
    assert result.business_recommendation != ""
    assert 0 <= result.confidence_score <= 1
    assert result.client_id == "test_client_001"
    
    print(f"✅ Prédiction: P={result.churn_probability:.4f}, "
          f"Decision={result.churn_prediction}, Risk={result.risk_level}")
    
    return result

def test_stable_client_prediction(predictor):
    """Test prédiction client stable"""
    print("🧪 Test Stable Client...")
    
    # Client fidèle et stable
    client_stable = {
        'contract': 'Two year',  # Contrat long terme
        'tenure': 48,  # Client fidèle 4 ans
        'monthly_charges': 65.0,  # Facture raisonnable
        'total_charges': 3120.0,
        'payment_method': 'Bank transfer (automatic)',  # Paiement automatique
        'internet_service': 'DSL',
        'paperless_billing': 'No'
    }
    
    result = predictor.predict_single(client_stable, "stable_client_001")
    
    print(f"✅ Client stable: P={result.churn_probability:.4f}, "
          f"Risk={result.risk_level}")
    
    # Client stable devrait avoir probabilité plus faible
    assert result.churn_probability < 0.7  # Seuil raisonnable
    
    return result

def test_batch_prediction(predictor):
    """Test prédiction par lot"""
    print("🧪 Test Batch Prediction...")
    
    clients_batch = [
        {
            'contract': 'Month-to-month',
            'tenure': 2,
            'monthly_charges': 75.0,
            'total_charges': 150.0,
            'payment_method': 'Electronic check',
            'internet_service': 'Fiber optic',
            'paperless_billing': 'Yes'
        },
        {
            'contract': 'Two year',
            'tenure': 36,
            'monthly_charges': 55.0,
            'total_charges': 1980.0,
            'payment_method': 'Credit card (automatic)',
            'internet_service': 'DSL',
            'paperless_billing': 'No'
        }
    ]
    
    client_ids = ["batch_001", "batch_002"]
    results = predictor.predict_batch(clients_batch, client_ids)
    
    assert len(results) == 2
    assert results[0].client_id == "batch_001"
    assert results[1].client_id == "batch_002"
    
    print(f"✅ Batch processing: {len(results)} prédictions terminées")
    
    for i, result in enumerate(results):
        print(f"   Client {i+1}: P={result.churn_probability:.4f}, Risk={result.risk_level}")
    
    return results

def test_model_info(predictor):
    """Test des informations modèle"""
    print("🧪 Test Model Info...")
    
    info = predictor.get_model_info()
    
    assert info["model_status"] == "loaded"
    assert "optimal_threshold" in info
    assert "features_count" in info
    
    print(f"✅ Model info: {info['model_type']}, Threshold: {info['optimal_threshold']:.4f}")
    
    return info

def test_health_check(predictor):
    """Test du health check"""
    print("🧪 Test Health Check...")
    
    health = predictor.health_check()
    
    assert health["status"] in ["healthy", "degraded", "unhealthy"]
    assert health["model_loaded"] == True
    assert "test_prediction_success" in health
    
    print(f"✅ Health status: {health['status']}")
    if health.get("test_prediction_success"):
        print(f"   Test prediction: {health.get('test_probability', 'N/A'):.4f}")
    
    return health

def test_result_serialization():
    """Test sérialisation des résultats"""
    print("🧪 Test Result Serialization...")
    
    predictor = ChurnPredictor()
    
    test_data = {
        'contract': 'One year',
        'tenure': 12,
        'monthly_charges': 70.0,
        'total_charges': 840.0,
        'payment_method': 'Mailed check',
        'internet_service': 'Fiber optic',
        'paperless_billing': 'Yes'
    }
    
    result = predictor.predict_single(test_data, "serialize_test")
    result_dict = result.to_dict()
    
    # Vérifications sérialisation
    assert isinstance(result_dict, dict)
    assert "churn_probability" in result_dict
    assert "client_id" in result_dict
    assert isinstance(result_dict["churn_probability"], float)
    
    print("✅ Sérialisation JSON OK")
    return result_dict

if __name__ == "__main__":
    print("🧪 VALIDATION DU MODEL WRAPPER")
    print("=" * 50)
    
    try:
        # Test 1: Chargement modèle
        predictor = test_model_loading()
        
        # Test 2: Prédiction unique
        result_risque = test_single_prediction(predictor)
        
        # Test 3: Client stable
        result_stable = test_stable_client_prediction(predictor)
        
        # Test 4: Prédiction batch
        batch_results = test_batch_prediction(predictor)
        
        # Test 5: Infos modèle
        model_info = test_model_info(predictor)
        
        # Test 6: Health check
        health_status = test_health_check(predictor)
        
        # Test 7: Sérialisation
        serialized_result = test_result_serialization()
        
        print("\n🎉 TOUS LES TESTS MODEL WRAPPER PASSÉS !")
        print("📋 Le wrapper est prêt pour l'intégration dans l'API FastAPI")
        
        print(f"\n📊 RÉSUMÉ DES TESTS:")
        print(f"   • Seuil optimal: {predictor.optimal_threshold:.4f}")
        print(f"   • Client risqué: {result_risque.churn_probability:.4f} → {result_risque.risk_level}")
        print(f"   • Client stable: {result_stable.churn_probability:.4f} → {result_stable.risk_level}")
        print(f"   • Health status: {health_status['status']}")
        
    except Exception as e:
        print(f"\n❌ ERREUR DANS LES TESTS: {e}")
        import traceback
        traceback.print_exc()
        raise