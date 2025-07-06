"""
Générateur de données clients fictives avec Faker
"""
import random
from faker import Faker
from typing import Dict, Union, List
from datetime import datetime
from config.settings import (
    CONTRACT_VALUES,
    PAYMENT_METHOD_VALUES,
    INTERNET_SERVICE_VALUES,
    PAPERLESS_BILLING_VALUES
)

# Initialisation Faker en français
fake = Faker('fr_FR')
Faker.seed(42)  # Pour reproductibilité en développement

class FakeClientGenerator:
    """Générateur de profils clients fictifs pour démonstration"""
    
    def __init__(self):
        # Probabilités réalistes basées sur votre analyse de données
        self.contract_weights = [0.55, 0.21, 0.24]  # Month-to-month, One year, Two year
        self.payment_weights = [0.22, 0.25, 0.33, 0.20]  # Bank, Credit, Electronic, Mailed
        self.internet_weights = [0.34, 0.44, 0.22]  # DSL, Fiber optic, No
        self.billing_weights = [0.40, 0.60]  # No, Yes
    
    def generate_random_client(self) -> Dict[str, Union[str, int, float]]:
        """
        Génère un client complètement aléatoire
        
        Returns:
            Dict avec toutes les features requises
        """
        # Génération aléatoire avec poids réalistes
        contract = fake.random_element(CONTRACT_VALUES)
        tenure = fake.random_int(min=0, max=72)
        
        # Facturation cohérente avec le type de contrat
        if contract == "Month-to-month":
            monthly_base = fake.random.uniform(65, 100)  # Plus cher
        elif contract == "One year":
            monthly_base = fake.random.uniform(50, 80)
        else:  # Two year
            monthly_base = fake.random.uniform(40, 70)  # Moins cher
        
        monthly_charges = round(monthly_base, 2)
        
        # Total charges cohérent avec tenure
        if tenure == 0:
            total_charges = 0.0  # Nouveau client
        else:
            # Variation réaliste autour de monthly * tenure
            expected_total = monthly_charges * tenure
            variation = fake.random.uniform(0.85, 1.15)  # ±15% de variation
            total_charges = round(expected_total * variation, 2)
        
        return {
            "contract": contract,
            "tenure": tenure,
            "monthly_charges": monthly_charges,
            "total_charges": total_charges,
            "payment_method": fake.random_element(PAYMENT_METHOD_VALUES),
            "internet_service": fake.random_element(INTERNET_SERVICE_VALUES),
            "paperless_billing": fake.random_element(PAPERLESS_BILLING_VALUES),
            "client_id": f"fake_{fake.random_int(10000, 99999)}"
        }
    
    def generate_high_risk_client(self) -> Dict[str, Union[str, int, float]]:
        """
        Génère un profil à haut risque de churn
        
        Returns:
            Dict avec features orientées risque élevé
        """
        # Caractéristiques à risque selon votre analyse
        contract = "Month-to-month"  # Plus risqué
        tenure = fake.random_int(min=0, max=12)  # Nouveaux/jeunes clients
        monthly_charges = fake.random.uniform(75, 118)  # Factures élevées
        payment_method = fake.random_element(["Electronic check", "Mailed check"])  # Paiements risqués
        internet_service = fake.random_element(["Fiber optic", "DSL"])  # Éviter "No"
        paperless_billing = "Yes"  # Corrélé avec risque dans vos données
        
        # Total charges cohérent
        if tenure == 0:
            total_charges = 0.0
        else:
            expected_total = monthly_charges * tenure
            total_charges = round(expected_total * fake.random.uniform(0.90, 1.10), 2)
        
        return {
            "contract": contract,
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": total_charges,
            "payment_method": payment_method,
            "internet_service": internet_service,
            "paperless_billing": paperless_billing,
            "client_id": f"high_risk_{fake.random_int(10000, 99999)}"
        }
    
    def generate_stable_client(self) -> Dict[str, Union[str, int, float]]:
        """
        Génère un profil client stable/fidèle
        
        Returns:
            Dict avec features orientées stabilité
        """
        # Caractéristiques de stabilité
        contract = fake.random_element(["One year", "Two year"])  # Contrats longs
        tenure = fake.random_int(min=24, max=72)  # Clients établis
        monthly_charges = fake.random.uniform(45, 75)  # Factures modérées
        payment_method = fake.random_element(["Bank transfer (automatic)", "Credit card (automatic)"])  # Paiements automatiques
        internet_service = fake.random_element(["DSL", "Fiber optic"])
        paperless_billing = fake.random_element(["Yes", "No"])  # Moins discriminant
        
        # Total charges réaliste pour client fidèle
        expected_total = monthly_charges * tenure
        total_charges = round(expected_total * fake.random.uniform(0.95, 1.05), 2)
        
        return {
            "contract": contract,
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": total_charges,
            "payment_method": payment_method,
            "internet_service": internet_service,
            "paperless_billing": paperless_billing,
            "client_id": f"stable_{fake.random_int(10000, 99999)}"
        }
    
    def generate_new_client(self) -> Dict[str, Union[str, int, float]]:
        """
        Génère un profil nouveau client (tenure = 0-3 mois)
        
        Returns:
            Dict représentant un nouveau client
        """
        tenure = fake.random_int(min=0, max=3)  # Très nouveau
        contract = fake.random_element(CONTRACT_VALUES)  # Tous types possibles
        monthly_charges = fake.random.uniform(50, 90)
        
        # Logique total charges pour nouveau client
        if tenure == 0:
            total_charges = 0.0  # Pas encore facturé
        else:
            total_charges = round(monthly_charges * tenure, 2)
        
        return {
            "contract": contract,
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": total_charges,
            "payment_method": fake.random_element(PAYMENT_METHOD_VALUES),
            "internet_service": fake.random_element(INTERNET_SERVICE_VALUES),
            "paperless_billing": fake.random_element(PAPERLESS_BILLING_VALUES),
            "client_id": f"new_{fake.random_int(10000, 99999)}"
        }
    
    def generate_premium_client(self) -> Dict[str, Union[str, int, float]]:
        """
        Génère un profil client premium (factures élevées, services premium)
        
        Returns:
            Dict représentant un client premium
        """
        contract = fake.random_element(["One year", "Two year"])  # Contrats premium
        tenure = fake.random_int(min=12, max=60)  # Clients établis
        monthly_charges = fake.random.uniform(85, 118)  # Factures élevées
        internet_service = "Fiber optic"  # Service premium
        payment_method = fake.random_element(["Bank transfer (automatic)", "Credit card (automatic)"])
        
        # Total charges cohérent avec profil premium
        expected_total = monthly_charges * tenure
        total_charges = round(expected_total * fake.random.uniform(0.98, 1.02), 2)
        
        return {
            "contract": contract,
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": total_charges,
            "payment_method": payment_method,
            "internet_service": internet_service,
            "paperless_billing": "Yes",  # Premium = digital
            "client_id": f"premium_{fake.random_int(10000, 99999)}"
        }
    
    def generate_client_by_type(self, profile_type: str = "random") -> Dict[str, Union[str, int, float]]:
        """
        Génère un client selon le type de profil demandé
        
        Args:
            profile_type: Type de profil à générer
            
        Returns:
            Dict avec les données client
            
        Raises:
            ValueError: Si le type de profil n'est pas reconnu
        """
        generators = {
            "random": self.generate_random_client,
            "high_risk": self.generate_high_risk_client,
            "stable": self.generate_stable_client,
            "new": self.generate_new_client,
            "premium": self.generate_premium_client
        }
        
        if profile_type not in generators:
            available_types = list(generators.keys())
            raise ValueError(f"Type de profil '{profile_type}' non reconnu. "
                           f"Types disponibles: {available_types}")
        
        return generators[profile_type]()
    
    def generate_multiple_clients(self, count: int = 10, 
                                profile_type: str = "random") -> List[Dict[str, Union[str, int, float]]]:
        """
        Génère plusieurs clients d'un type donné
        
        Args:
            count: Nombre de clients à générer
            profile_type: Type de profil
            
        Returns:
            List[Dict]: Liste des clients générés
        """
        return [self.generate_client_by_type(profile_type) for _ in range(count)]
    
    def get_available_profile_types(self) -> List[str]:
        """Retourne la liste des types de profils disponibles"""
        return ["random", "high_risk", "stable", "new", "premium"]
    
    def get_profile_description(self, profile_type: str) -> str:
        """
        Retourne la description d'un type de profil
        
        Args:
            profile_type: Type de profil
            
        Returns:
            str: Description du profil
        """
        descriptions = {
            "random": "Profil complètement aléatoire avec distribution réaliste",
            "high_risk": "Profil à haut risque de churn (nouveau client, month-to-month, facture élevée)",
            "stable": "Profil client fidèle (contrat long terme, ancienneté élevée, paiement automatique)",
            "new": "Nouveau client (0-3 mois d'ancienneté)",
            "premium": "Client premium (services haut de gamme, factures élevées)"
        }
        return descriptions.get(profile_type, "Type de profil non reconnu")

# Instance globale du générateur
fake_client_generator = FakeClientGenerator()

# Fonctions utilitaires pour l'API
def generate_fake_client(profile_type: str = "random") -> Dict[str, Union[str, int, float]]:
    """
    Fonction utilitaire pour générer un client fictif
    
    Args:
        profile_type: Type de profil à générer
        
    Returns:
        Dict avec les données client
    """
    return fake_client_generator.generate_client_by_type(profile_type)

def get_available_profile_types() -> List[str]:
    """Retourne les types de profils disponibles"""
    return fake_client_generator.get_available_profile_types()

def get_profile_description(profile_type: str) -> str:
    """Retourne la description d'un type de profil"""
    return fake_client_generator.get_profile_description(profile_type)