"""
Churn Prediction Dashboard - Version Streamlit Cloud
Interface utilisant les classes ChurnPredictor et ChurnPreprocessor existantes
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math
import json
from datetime import datetime
from typing import Dict, Any, List
from faker import Faker

# Imports de vos modules
from src.model_wrapper import ChurnPredictor, ChurnPredictionResult
from src.preprocessing import ChurnPreprocessor
from config.settings import (
    STREAMLIT_CONFIG, 
    CONTRACT_VALUES, 
    PAYMENT_METHOD_VALUES,
    INTERNET_SERVICE_VALUES,
    PAPERLESS_BILLING_VALUES,
    FAKER_PROFILES
)

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(**STREAMLIT_CONFIG)

# CSS personnalisé élégant
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CHARGEMENT DES INSTANCES AVEC CACHE
# =====================================================

@st.cache_resource
def load_predictor():
    """Charge le prédicteur avec cache Streamlit"""
    try:
        predictor = ChurnPredictor()
        return predictor
    except Exception as e:
        st.error(f"❌ Erreur chargement modèle: {e}")
        return None

@st.cache_resource  
def load_preprocessor():
    """Charge le preprocessor avec cache Streamlit"""
    try:
        preprocessor = ChurnPreprocessor()
        return preprocessor
    except Exception as e:
        st.error(f"❌ Erreur chargement preprocessor: {e}")
        return None

# Chargement des instances
predictor = load_predictor()
preprocessor = load_preprocessor()

# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================

class FakeClientGenerator:
    """Générateur de clients fictifs pour la démo"""
    
    def __init__(self):
        self.fake = Faker('fr_FR')
        
    def generate_client(self, profile_type: str = "random") -> Dict[str, Any]:
        """Génère un client fictif selon le profil"""
        if profile_type == "high_risk":
            return self._generate_high_risk()
        elif profile_type == "stable":
            return self._generate_stable()
        elif profile_type == "new":
            return self._generate_new()
        elif profile_type == "premium":
            return self._generate_premium()
        else:
            return self._generate_random()
    
    def _generate_high_risk(self) -> Dict[str, Any]:
        """Client à haut risque"""
        tenure = self.fake.random_int(0, 12)
        monthly_charges = self.fake.random.uniform(80, 118)
        total_charges = monthly_charges * max(tenure, 1) + self.fake.random.uniform(-100, 100)
        total_charges = max(total_charges, 0)
        
        return {
            "contract": "Month-to-month",
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": round(total_charges, 2),
            "payment_method": "Electronic check",
            "internet_service": self.fake.random_element(["Fiber optic", "DSL"]),
            "paperless_billing": self.fake.random_element(["Yes", "No"])
        }
    
    def _generate_stable(self) -> Dict[str, Any]:
        """Client stable"""
        tenure = self.fake.random_int(24, 72)
        monthly_charges = self.fake.random.uniform(35, 75)
        total_charges = monthly_charges * tenure + self.fake.random.uniform(-50, 200)
        total_charges = max(total_charges, monthly_charges)
        
        return {
            "contract": self.fake.random_element(["One year", "Two year"]),
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": round(total_charges, 2),
            "payment_method": self.fake.random_element([
                "Bank transfer (automatic)", 
                "Credit card (automatic)"
            ]),
            "internet_service": self.fake.random_element(["DSL", "Fiber optic"]),
            "paperless_billing": "Yes"
        }
    
    def _generate_new(self) -> Dict[str, Any]:
        """Nouveau client"""
        tenure = self.fake.random_int(0, 3)
        monthly_charges = self.fake.random.uniform(25, 85)
        
        if tenure == 0:
            total_charges = 0
        else:
            total_charges = monthly_charges * tenure + self.fake.random.uniform(-20, 50)
            total_charges = max(total_charges, 0)
        
        return {
            "contract": self.fake.random_element(CONTRACT_VALUES),
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": round(total_charges, 2),
            "payment_method": self.fake.random_element(PAYMENT_METHOD_VALUES),
            "internet_service": self.fake.random_element(INTERNET_SERVICE_VALUES),
            "paperless_billing": self.fake.random_element(PAPERLESS_BILLING_VALUES)
        }
    
    def _generate_premium(self) -> Dict[str, Any]:
        """Client premium"""
        tenure = self.fake.random_int(12, 48)
        monthly_charges = self.fake.random.uniform(85, 118)
        total_charges = monthly_charges * tenure + self.fake.random.uniform(0, 500)
        
        return {
            "contract": self.fake.random_element(["One year", "Two year", "Month-to-month"]),
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": round(total_charges, 2),
            "payment_method": self.fake.random_element([
                "Credit card (automatic)",
                "Bank transfer (automatic)"
            ]),
            "internet_service": "Fiber optic",
            "paperless_billing": "Yes"
        }
    
    def _generate_random(self) -> Dict[str, Any]:
        """Client aléatoire"""
        tenure = self.fake.random_int(0, 72)
        monthly_charges = self.fake.random.uniform(18.25, 118.75)
        
        if tenure == 0:
            total_charges = 0
        else:
            base_total = monthly_charges * tenure
            variation = self.fake.random.uniform(-200, 300)
            total_charges = max(base_total + variation, 0)
        
        return {
            "contract": self.fake.random_element(CONTRACT_VALUES),
            "tenure": tenure,
            "monthly_charges": round(monthly_charges, 2),
            "total_charges": round(total_charges, 2),
            "payment_method": self.fake.random_element(PAYMENT_METHOD_VALUES),
            "internet_service": self.fake.random_element(INTERNET_SERVICE_VALUES),
            "paperless_billing": self.fake.random_element(PAPERLESS_BILLING_VALUES)
        }

@st.cache_resource
def get_faker_generator():
    """Instance du générateur avec cache"""
    return FakeClientGenerator()

faker_gen = get_faker_generator()

def create_risk_gauge(probability: float, risk_level: str, optimal_threshold: float) -> go.Figure:
    """Crée un gauge de risque élégant"""
    # Couleur selon le niveau de risque
    if "Critical" in risk_level or "High" in risk_level:
        gauge_color = "#dc3545"
    elif "Medium" in risk_level:
        gauge_color = "#ffc107"
    else:
        gauge_color = "#28a745"
    
    # Calcul position seuil
    seuil_value = optimal_threshold * 100
    angle_degrees = 180 - (seuil_value / 100 * 180)
    angle_radians = math.radians(angle_degrees)
    
    rayon = 0.55
    center_x, center_y = 0.5, 0.3
    text_x = center_x + rayon * math.cos(angle_radians)
    text_y = center_y + rayon * math.sin(angle_radians) + 0.08
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {
            'text': "<b>Risque de Churn</b>",
            'font': {'size': 20, 'color': 'darkblue'}
        },
        number = {
            'font': {'size': 36, 'color': gauge_color},
            'suffix': '%'
        },
        gauge = {
            'axis': {
                'range': [None, 100], 
                'tickwidth': 0,
                'tickcolor': "white",
                'ticktext': [],
                'tickvals': []
            },
            'bar': {'color': gauge_color, 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "lightgray",
            'steps': [
                {'range': [0, seuil_value], 'color': '#d4edda'},
                {'range': [seuil_value, 65], 'color': '#fff3cd'},
                {'range': [65, 100], 'color': '#f8d7da'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 1.0,
                'value': seuil_value
            }
        }
    ))
    
    # Annotation du seuil
    fig.add_annotation(
        x=text_x + 0.03, y=text_y + 0.05,  # Position remontée encore plus (+0.08)
        text="<b>Seuil de churn : 35.1%</b>",  # Texte complet avec label
        
        font=dict(size=15, color="blue", family="Arial"),  # Police 13pt
        # Suppression du fond de couleur
        bgcolor=None,  # Pas de fond
        bordercolor=None,  # Pas de bordure
        borderwidth=0
    )
    
    fig.update_layout(
        height=280,
        font={'color': "darkblue", 'family': "Arial"},
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=40)
    )
    
    return fig

def create_confidence_bar(confidence: float) -> go.Figure:
    """Crée une barre de confiance"""
    if confidence >= 0.8:
        color = "#28a745"
        level = "Très élevée"
    elif confidence >= 0.6:
        color = "#17a2b8"
        level = "Élevée"
    elif confidence >= 0.4:
        color = "#ffc107"
        level = "Moyenne"
    else:
        color = "#dc3545"
        level = "Faible"
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[confidence * 100],
        y=['Confiance'],
        orientation='h',
        marker_color=color,
        text=[f'{confidence*100:.1f}% - {level}'],
        textposition='auto',
        textfont={'size': 14, 'color': 'white'}
    ))
    
    fig.update_layout(
        title="<b>Confiance du Modèle</b>",
        xaxis={'range': [0, 100], 'title': '', 'showticklabels': False},
        yaxis={'title': '', 'showticklabels': False},
        height=120,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_recommendation_timeline(risk_level: str) -> go.Figure:
    """Crée un plan d'action sous forme de tableau"""
    if "Critical" in risk_level:
        actions = [
            {"action": "🚨 Contact téléphonique urgent", "deadline": "Immédiat", "priority": 1},
            {"action": "💰 Offre de rétention personnalisée", "deadline": "24 heures", "priority": 2},
            {"action": "📋 Analyse détaillée des besoins", "deadline": "48 heures", "priority": 3}
        ]
        main_color = "#dc3545"
    elif "High" in risk_level:
        actions = [
            {"action": "📞 Contact commercial prioritaire", "deadline": "48 heures", "priority": 1},
            {"action": "📊 Enquête satisfaction approfondie", "deadline": "1 semaine", "priority": 2},
            {"action": "🎯 Mise en place suivi personnalisé", "deadline": "2 semaines", "priority": 3}
        ]
        main_color = "#ffc107"
    elif "Medium" in risk_level:
        actions = [
            {"action": "📈 Surveillance comportement renforcée", "deadline": "1 semaine", "priority": 1},
            {"action": "📧 Campagne email ciblée", "deadline": "2 semaines", "priority": 2},
            {"action": "💬 Enquête satisfaction standard", "deadline": "1 mois", "priority": 3}
        ]
        main_color = "#17a2b8"
    else:
        actions = [
            {"action": "📊 Monitoring standard mensuel", "deadline": "1 mois", "priority": 1},
            {"action": "📮 Newsletter personnalisée", "deadline": "2 mois", "priority": 2},
            {"action": "🔄 Préparation renouvellement", "deadline": "3 mois", "priority": 3}
        ]
        main_color = "#28a745"
    
    fig = go.Figure()
    
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Priorité</b>", "<b>Action Recommandée</b>", "<b>Délai</b>"],
            fill_color=main_color,
            font=dict(color='white', size=16),
            align='center',
            height=40
        ),
        cells=dict(
            values=[
                [f"#{action['priority']}" for action in actions],
                [action['action'] for action in actions],
                [action['deadline'] for action in actions]
            ],
            fill_color=['lightgray', 'white', 'lightblue'],
            font=dict(color='darkblue', size=14),
            align=['center', 'left', 'center'],
            height=35
        )
    ))
    
    fig.update_layout(
        title="<b>📅 Plan d'Action Recommandé</b>",
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def format_client_data_display(client_data: Dict[str, Any]) -> str:
    """Formate les données client pour affichage"""
    return f"""
    **📋 Profil Client:**
    - **Contrat:** {client_data.get('contract', 'N/A')}
    - **Ancienneté:** {client_data.get('tenure', 'N/A')} mois
    - **Facturation:** {client_data.get('monthly_charges', 'N/A')}€/mois
    - **Total facturé:** {client_data.get('total_charges', 'N/A')}€
    - **Paiement:** {client_data.get('payment_method', 'N/A')}
    - **Internet:** {client_data.get('internet_service', 'N/A')}
    - **Facture numérique:** {client_data.get('paperless_billing', 'N/A')}
    """

# =====================================================
# GESTION HISTORIQUE
# =====================================================

def save_prediction_to_history(client_data: Dict[str, Any], result: ChurnPredictionResult):
    """Sauvegarde dans l'historique"""
    if "prediction_history" not in st.session_state:
        st.session_state.prediction_history = []
    
    history_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "client_data": client_data,
        "result": result.to_dict(),
        "id": len(st.session_state.prediction_history) + 1
    }
    
    st.session_state.prediction_history.append(history_entry)
    
    if len(st.session_state.prediction_history) > 50:
        st.session_state.prediction_history = st.session_state.prediction_history[-50:]

def get_prediction_history() -> List[Dict[str, Any]]:
    """Récupère l'historique"""
    return st.session_state.get("prediction_history", [])

def clear_prediction_history():
    """Vide l'historique"""
    st.session_state.prediction_history = []

# =====================================================
# HEADER PRINCIPAL
# =====================================================

st.markdown('<h1 class="main-header">Churn Prediction Dashboard</h1>', unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
    <p>Prédiction intelligente du risque de churn client 🤖</p>
    <p style="color: #888; font-size: 0.9rem;">
        Modèle XGBoost optimisé • Seuil business adaptatif • 11 features engineered
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

# Status en haut
with st.sidebar.container():
    if predictor and predictor.is_loaded:
        health = predictor.health_check()
        if health["status"] == "healthy":
            st.markdown("""
            <div style="
                background-color: #155724; 
                color: white; 
                padding: 0.75rem; 
                border-radius: 0.5rem; 
                margin-bottom: 1rem; 
                text-align: center;
                font-weight: bold;
            ">
                🟢 Modèle XGBoost Chargé
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background-color: #721c24; 
                color: white; 
                padding: 0.75rem; 
                border-radius: 0.5rem; 
                margin-bottom: 1rem; 
                text-align: center;
                font-weight: bold;
            ">
                🔴 Problème Modèle
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("🚨 Erreur : Modèle non chargé")

# Navigation
st.sidebar.markdown("### 📍 Section")
page = st.sidebar.selectbox(
    "",
    ["🏠 Prédiction", "📊 Historique", "ℹ️ Modèle", "🎭 Démonstration"],
    label_visibility="collapsed"
)

# Boutons info
st.sidebar.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📋 Détails Modèle", use_container_width=True):
        if predictor:
            health = predictor.health_check()
            st.sidebar.json(health)

with col2:
    if st.button("ℹ️ Infos Système", use_container_width=True):
        if predictor:
            model_info = predictor.get_model_info()
            st.sidebar.success("✅ Système opérationnel")
            st.sidebar.write(f"**Seuil:** {model_info.get('optimal_threshold', 'N/A'):.4f}")
            st.sidebar.write(f"**Features:** {model_info.get('features_count', 'N/A')}")

# =====================================================
# VÉRIFICATION MODULES
# =====================================================

if not predictor or not predictor.is_loaded:
    st.error("🚨 **Erreur critique:** Le modèle n'est pas chargé correctement.")
    st.info("Vérifiez que tous les fichiers sont présents dans les dossiers models/ et encoders/")
    st.stop()

# =====================================================
# INITIALISATION SESSION STATE
# =====================================================

form_fields = ['contract', 'tenure', 'monthly_charges', 'total_charges', 
               'payment_method', 'internet_service', 'paperless_billing']

default_values = {
    "contract": "Month-to-month",
    "tenure": 12,
    "monthly_charges": 75.0,
    "total_charges": 900.0,
    "payment_method": "Electronic check",
    "internet_service": "Fiber optic", 
    "paperless_billing": "Yes"
}

for field in form_fields:
    if field not in st.session_state:
        st.session_state[field] = default_values[field]

# =====================================================
# PAGE PRINCIPALE - PRÉDICTION
# =====================================================

if page == "🏠 Prédiction":
    st.markdown("## 📝 Informations Client")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Saisie Manuelle")
        
        with st.form("client_form"):
            # Ligne 1
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                contract = st.selectbox(
                    "Type de Contrat",
                    CONTRACT_VALUES,
                    index=CONTRACT_VALUES.index(st.session_state.contract),
                    key="form_contract"
                )
            
            with col1_2:
                tenure = st.number_input(
                    "Ancienneté (mois)",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.tenure,
                    key="form_tenure"
                )
            
            # Ligne 2
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                monthly_charges = st.number_input(
                    "Facturation mensuelle (€)",
                    min_value=0.01,
                    max_value=200.0,
                    value=st.session_state.monthly_charges,
                    step=0.01,
                    key="form_monthly_charges"
                )
            
            with col2_2:
                total_charges = st.number_input(
                    "Total facturé (€)",
                    min_value=0.0,
                    max_value=10000.0,
                    value=st.session_state.total_charges,
                    step=0.01,
                    key="form_total_charges"
                )
            
            # Ligne 3
            col3_1, col3_2 = st.columns(2)
            with col3_1:
                payment_method = st.selectbox(
                    "Mode de Paiement",
                    PAYMENT_METHOD_VALUES,
                    index=PAYMENT_METHOD_VALUES.index(st.session_state.payment_method),
                    key="form_payment_method"
                )
            
            with col3_2:
                internet_service = st.selectbox(
                    "Service Internet",
                    INTERNET_SERVICE_VALUES,
                    index=INTERNET_SERVICE_VALUES.index(st.session_state.internet_service),
                    key="form_internet_service"
                )
            
            # Ligne 4
            paperless_billing = st.selectbox(
                "Facturation Numérique",
                PAPERLESS_BILLING_VALUES,
                index=PAPERLESS_BILLING_VALUES.index(st.session_state.paperless_billing),
                key="form_paperless_billing"
            )
            
            # Bouton prédiction
            predict_button = st.form_submit_button(
                "Prédire le Risque de Churn",
                type="primary"
            )
    
    with col2:
        st.markdown("### 🎭 Clients Fictifs")
        st.markdown("*Générez des profils types pour tester le modèle*")
        
        for profile_type, info in FAKER_PROFILES.items():
            if st.button(
                f"{info['name']}",
                key=f"btn_{profile_type}",
                help=info['description'],
                use_container_width=True
            ):
                with st.spinner(f"Génération profil {info['name']}..."):
                    fake_data = faker_gen.generate_client(profile_type)
                    
                    # Mise à jour session_state
                    for field in form_fields:
                        if field in fake_data:
                            st.session_state[field] = fake_data[field]
                    
                    st.success(f"✅ Profil {info['name']} généré!")
                    st.rerun()
        
        # Reset
        if st.button("🔄 Reset Formulaire", use_container_width=True):
            for field in form_fields:
                st.session_state[field] = default_values[field]
            st.rerun()
    
    # =====================================================
    # TRAITEMENT PRÉDICTION
    # =====================================================
    
    if predict_button:
        client_data = {
            "contract": contract,
            "tenure": tenure,
            "monthly_charges": monthly_charges,
            "total_charges": total_charges,
            "payment_method": payment_method,
            "internet_service": internet_service,
            "paperless_billing": paperless_billing
        }
        
        # Affichage données
        with st.expander("📋 Données Client Saisies"):
            st.markdown(format_client_data_display(client_data))
        
        # Prédiction
        with st.spinner("🔄 Analyse en cours..."):
            try:
                result = predictor.predict_single(
                    client_data, 
                    f"streamlit_client_{datetime.now().strftime('%H%M%S')}"
                )
                
                # Affichage résultats
                st.markdown("## 📈 Résultats de l'Analyse")
                
                # Métriques
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Probabilité Churn", f"{result.churn_probability*100:.1f}%")
                
                with col2:
                    prediction_text = "🚨 Churn Prédit" if result.churn_prediction == 1 else "✅ Client Stable"
                    st.metric("Prédiction", prediction_text)
                
                with col3:
                    st.metric("Confiance", f"{result.confidence_score*100:.1f}%")
                
                # Niveau de risque
                risk_colors = {
                    "Critical Risk": "#dc3545",
                    "High Risk": "#dc3545", 
                    "Medium-High Risk": "#ffc107",
                    "Medium Risk": "#ffc107",
                    "Low-Medium Risk": "#17a2b8",
                    "Low Risk": "#28a745"
                }
                risk_color = risk_colors.get(result.risk_level, "#17a2b8")
                
                st.markdown(
                    f"""
                    <div style="background-color: {risk_color}20; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        <h3 style="color: {risk_color}; margin: 0;">
                            {result.risk_level}
                        </h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Recommandation
                st.info(f"💡 **Recommandation:** {result.business_recommendation}")
                
                # Graphiques
                col1, col2 = st.columns(2)
                
                with col1:
                    gauge_fig = create_risk_gauge(
                        result.churn_probability, 
                        result.risk_level,
                        predictor.optimal_threshold
                    )
                    st.plotly_chart(gauge_fig, use_container_width=True)
                
                with col2:
                    confidence_fig = create_confidence_bar(result.confidence_score)
                    st.plotly_chart(confidence_fig, use_container_width=True)
                
                # Timeline
                timeline_fig = create_recommendation_timeline(result.risk_level)
                st.plotly_chart(timeline_fig, use_container_width=True)
                
                # Sauvegarde
                save_prediction_to_history(client_data, result)
                st.success("💾 Prédiction sauvegardée dans l'historique")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse: {str(e)}")

# =====================================================
# PAGE HISTORIQUE
# =====================================================

elif page == "📊 Historique":
    st.markdown("## 📊 Historique des Prédictions")
    
    history = get_prediction_history()
    
    if not history:
        st.info("📭 Aucune prédiction dans l'historique. Effectuez une prédiction pour commencer!")
    else:
        # Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre de Prédictions", len(history))
        
        with col2:
            if st.button("🗑️ Vider l'Historique"):
                clear_prediction_history()
                st.rerun()
        
        with col3:
            if st.button("💾 Exporter JSON"):
                export_data = json.dumps(history, indent=2, ensure_ascii=False)
                st.download_button(
                    "⬇️ Télécharger",
                    export_data,
                    file_name=f"churn_predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )
        
        # Affichage historique
        st.markdown("### 📋 Dernières Prédictions")
        
        for entry in reversed(history[-10:]):
            with st.expander(f"🕐 {entry['timestamp']} - ID: {entry['id']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📋 Client:**")
                    st.markdown(format_client_data_display(entry['client_data']))
                
                with col2:
                    result_data = entry['result']
                    st.markdown("**📈 Résultat:**")
                    st.write(f"**Probabilité:** {result_data['churn_probability']*100:.1f}%")
                    st.write(f"**Risque:** {result_data['risk_level']}")
                    st.write(f"**Confiance:** {result_data['confidence_score']*100:.1f}%")

# =====================================================
# PAGE INFORMATIONS MODÈLE
# =====================================================

elif page == "ℹ️ Modèle":
    st.markdown("## 🤖 Informations du Modèle")
    
    model_info = predictor.get_model_info()
    
    # Informations générales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Type de Modèle", model_info.get('model_type', 'N/A'))
    
    with col2:
        st.metric("Seuil Optimal", f"{model_info.get('optimal_threshold', 0):.4f}")
    
    with col3:
        st.metric("Nombre de Features", model_info.get('features_count', 'N/A'))
    
    # Métriques de performance
    if 'model_metrics' in model_info:
        st.markdown("### 📊 Métriques de Performance")
        
        metrics = model_info['model_metrics']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Recall", f"{metrics.get('recall', 0):.3f}")
        
        with col2:
            st.metric("Precision", f"{metrics.get('precision', 0):.3f}")
        
        with col3:
            st.metric("Business Score", f"{metrics.get('business_score', 0):.4f}")
        
        with col4:
            st.metric("AUC", f"{metrics.get('auc_score', 0):.3f}")
    
    # Health check
    st.markdown("### 🔧 Status Système")
    health = predictor.health_check()
    
    if health["status"] == "healthy":
        st.success("✅ Système opérationnel")
        st.info(f"Test probability: {health.get('test_probability', 'N/A'):.4f}")
    else:
        st.error(f"❌ Problème système: {health.get('test_error', 'Inconnu')}")
    
    # Infos détaillées
    with st.expander("📄 Informations Complètes"):
        st.json(model_info)

# =====================================================
# PAGE DÉMONSTRATION  
# =====================================================

elif page == "🎭 Démonstration":
    st.markdown("## 🎭 Démonstration Interactive")
    
    st.markdown("""
    Cette section permet de tester rapidement différents profils clients 
    et d'observer les variations de prédictions.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        profile_type = st.selectbox(
            "Type de Profil",
            list(FAKER_PROFILES.keys()),
            format_func=lambda x: FAKER_PROFILES[x]["name"]
        )
        
        st.info(f"📝 {FAKER_PROFILES[profile_type]['description']}")
    
    with col2:
        num_profiles = st.slider("Nombre de Profils", 1, 5, 3)
    
    if st.button("🎲 Générer et Prédire"):
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(num_profiles):
            status_text.text(f"Génération et analyse profil {i+1}/{num_profiles}...")
            progress_bar.progress((i+1) / num_profiles)
            
            try:
                fake_data = faker_gen.generate_client(profile_type)
                result = predictor.predict_single(fake_data, f"demo_{i+1}")
                
                results.append({
                    "client": fake_data,
                    "result": result
                })
            except Exception as e:
                st.error(f"Erreur profil {i+1}: {str(e)}")
        
        status_text.text("✅ Analyse terminée!")
        progress_bar.empty()
        status_text.empty()
        
        # Affichage résultats
        if results:
            st.markdown("### 📊 Résultats de la Démonstration")
            
            for i, data in enumerate(results):
                with st.expander(f"Client {i+1} - {data['result'].client_id}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Profil:**")
                        st.markdown(format_client_data_display(data['client']))
                    
                    with col2:
                        st.markdown("**Prédiction:**")
                        result = data['result']
                        
                        risk_color = "🔴" if result.churn_prediction == 1 else "🟢"
                        st.markdown(f"{risk_color} **{result.risk_level}**")
                        st.markdown(f"**Probabilité:** {result.churn_probability*100:.1f}%")
                        st.markdown(f"**Confiance:** {result.confidence_score*100:.1f}%")
                        
                        st.info(f"💡 {result.business_recommendation}")
            
            # Statistiques
            if len(results) > 1:
                st.markdown("### 📈 Statistiques de Démonstration")
                
                probabilities = [r['result'].churn_probability for r in results]
                high_risk = sum(1 for r in results if r['result'].churn_prediction == 1)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Probabilité Moyenne", f"{sum(probabilities)/len(probabilities)*100:.1f}%")
                
                with col2:
                    st.metric("Clients à Risque", f"{high_risk}/{len(results)}")
                
                with col3:
                    if probabilities:
                        std_dev = (sum((p-sum(probabilities)/len(probabilities))**2 for p in probabilities)/len(probabilities))**0.5
                        st.metric("Écart-type", f"{std_dev*100:.1f}%")

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>Churn Prediction Dashboard | Modèle XGBoost Champion | Version Streamlit Cloud</p>
    <p>Développé avec ❤️ pour la prédiction intelligente de churn client</p>
</div>
""", unsafe_allow_html=True)