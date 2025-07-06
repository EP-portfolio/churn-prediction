"""
Fonctions utilitaires pour l'application Streamlit
"""
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

from config import API_ENDPOINTS, API_TIMEOUT, COLORS, RISK_MESSAGES, RISK_THRESHOLDS

# =====================================================
# FONCTIONS API
# =====================================================

@st.cache_data(ttl=300)
def check_api_health() -> Dict[str, Any]:
    """
    Vérifie la santé de l'API FastAPI
    
    Returns:
        Dict avec status de l'API
    """
    try:
        response = requests.get(API_ENDPOINTS["health"], timeout=10)
        if response.status_code == 200:
            return {
                "status": "healthy",
                "data": response.json()
            }
        else:
            return {
                "status": "unhealthy", 
                "error": f"HTTP {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "status": "offline",
            "error": "API inaccessible (vérifiez que docker-compose up est lancé)"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@st.cache_data(ttl=300)
def get_model_info() -> Optional[Dict[str, Any]]:
    """
    Récupère les informations du modèle
    
    Returns:
        Dict avec infos du modèle ou None si erreur
    """
    try:
        response = requests.get(API_ENDPOINTS["model_info"], timeout=API_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def call_prediction_api(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appelle l'API de prédiction
    
    Args:
        client_data: Données du client
        
    Returns:
        Dict avec résultat de prédiction
    """
    try:
        response = requests.post(
            API_ENDPOINTS["predict"],
            json=client_data,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Erreur API: {response.status_code}",
                "details": response.text[:200]
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "API non accessible",
            "details": "Vérifiez que l'API FastAPI est lancée (docker-compose up)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Erreur réseau",
            "details": str(e)
        }

def generate_fake_client(profile_type: str = "random") -> Dict[str, Any]:
    """
    Génère un client fictif via l'API
    
    Args:
        profile_type: Type de profil à générer
        
    Returns:
        Dict avec données du client fictif
    """
    try:
        response = requests.get(
            f"{API_ENDPOINTS['fake_client']}?profile_type={profile_type}",
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Erreur génération: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False, 
            "error": f"Erreur réseau: {str(e)}"
        }

# =====================================================
# FONCTIONS DE VISUALISATION
# =====================================================

def create_risk_gauge(probability: float, risk_level: str, confidence: float) -> go.Figure:
    """
    Crée un gauge de risque de churn avec seuil positionné au-dessus
    
    Args:
        probability: Probabilité de churn [0-1]
        risk_level: Niveau de risque textuel
        confidence: Score de confiance
        
    Returns:
        Figure Plotly
    """
    # Couleur selon le niveau de risque
    if "Critical" in risk_level or "High" in risk_level:
        gauge_color = COLORS["high"]
    elif "Medium" in risk_level:
        gauge_color = COLORS["medium"]
    else:
        gauge_color = COLORS["stable"]
    
    # CALCUL POSITION AUTOMATIQUE DU SEUIL - AU-DESSUS DU GAUGE
    seuil_value = 35.1  # Valeur du seuil
    
    # Pour un gauge demi-cercle : 0% = position 180°, 100% = position 0°
    import math
    
    # Angle en radians pour la position du seuil (35.1%)
    angle_degrees = 180 - (seuil_value / 100 * 180)
    angle_radians = math.radians(angle_degrees)
    
    # Coordonnées pour positionner le texte AU-DESSUS du gauge
    rayon = 0.55  # Augmenté pour être au-dessus du gauge (était 0.45)
    center_x, center_y = 0.5, 0.3  # Centre approximatif du gauge demi-cercle
    
    # Calcul des coordonnées x,y basées sur l'angle
    text_x = center_x + rayon * math.cos(angle_radians)
    text_y = center_y + rayon * math.sin(angle_radians) + 0.05  # +0.05 pour être encore plus au-dessus
    
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
                {'range': [0, 35.1], 'color': '#d4edda'},
                {'range': [35.1, 65], 'color': '#fff3cd'},
                {'range': [65, 100], 'color': '#f8d7da'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 1.0,
                'value': 35.1
            }
        }
    ))
    
    # ANNOTATION POSITIONNÉE PLUS HAUT AVEC TEXTE COMPLET
    fig.add_annotation(
        x=text_x + 0.01, y=text_y + 0.04,  # Position remontée encore plus (+0.08)
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
    """
    Crée un graphique de confiance simplifié
    
    Args:
        confidence: Score de confiance [0-1]
        
    Returns:
        Figure Plotly
    """
    # Couleur selon le niveau de confiance
    if confidence >= 0.8:
        color = COLORS["success"]
        level = "Très élevée"
    elif confidence >= 0.6:
        color = COLORS["info"]
        level = "Élevée"
    elif confidence >= 0.4:
        color = COLORS["warning"]
        level = "Moyenne"
    else:
        color = COLORS["danger"]
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
        xaxis={
            'range': [0, 100], 
            'title': '',  # Suppression du titre de l'axe
            'showticklabels': False  # Suppression des valeurs 0,50,100
        },
        yaxis={'title': '', 'showticklabels': False},  # Suppression de "Confiance"
        height=120,  # Hauteur réduite
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_features_radar(client_data: Dict[str, Any]) -> go.Figure:
    """
    Crée un graphique radar des caractéristiques client
    
    Args:
        client_data: Données du client
        
    Returns:
        Figure Plotly
    """
    # Normalisation des features pour le radar
    features = [
        'Ancienneté (mois)',
        'Facturation mensuelle', 
        'Type de contrat',
        'Service Internet',
        'Mode de paiement'
    ]
    
    # Valeurs normalisées [0-100]
    values = [
        min(client_data.get('tenure', 0) / 72 * 100, 100),  # Max 72 mois
        min(client_data.get('monthly_charges', 0) / 118 * 100, 100),  # Max 118€
        50 if client_data.get('contract') == 'Month-to-month' else 80,  # Contrat
        70 if 'Fiber' in str(client_data.get('internet_service', '')) else 30,  # Internet
        30 if 'Electronic' in str(client_data.get('payment_method', '')) else 70  # Paiement
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=features,
        fill='toself',
        name='Profil Client',
        line_color=COLORS["primary"],
        fillcolor=f"rgba(31, 119, 180, 0.3)"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="<b>Profil Client</b>",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_recommendation_timeline(risk_level: str, business_recommendation: str) -> go.Figure:
    """
    Crée un plan d'action avec priorités et deadlines temporelles - Police augmentée
    
    Args:
        risk_level: Niveau de risque
        business_recommendation: Recommandation business
        
    Returns:
        Figure Plotly avec plan d'action ordonné
    """
    # Actions selon le niveau de risque avec deadlines
    if "Critical" in risk_level:
        actions = [
            {"action": "🚨 Contact téléphonique urgent", "deadline": "Immédiat", "priority": 1},
            {"action": "💰 Offre de rétention personnalisée", "deadline": "24 heures", "priority": 2},
            {"action": "📋 Analyse détaillée des besoins", "deadline": "48 heures", "priority": 3}
        ]
        main_color = COLORS["danger"]
    elif "High" in risk_level:
        actions = [
            {"action": "📞 Contact commercial prioritaire", "deadline": "48 heures", "priority": 1},
            {"action": "📊 Enquête satisfaction approfondie", "deadline": "1 semaine", "priority": 2},
            {"action": "🎯 Mise en place suivi personnalisé", "deadline": "2 semaines", "priority": 3}
        ]
        main_color = COLORS["warning"]
    elif "Medium" in risk_level:
        actions = [
            {"action": "📈 Surveillance comportement renforcée", "deadline": "1 semaine", "priority": 1},
            {"action": "📧 Campagne email ciblée", "deadline": "2 semaines", "priority": 2},
            {"action": "💬 Enquête satisfaction standard", "deadline": "1 mois", "priority": 3}
        ]
        main_color = COLORS["info"]
    else:
        actions = [
            {"action": "📊 Monitoring standard mensuel", "deadline": "1 mois", "priority": 1},
            {"action": "📮 Newsletter personnalisée", "deadline": "2 mois", "priority": 2},
            {"action": "🔄 Préparation renouvellement", "deadline": "3 mois", "priority": 3}
        ]
        main_color = COLORS["success"]
    
    # Création d'un tableau avec police augmentée
    fig = go.Figure()
    
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Priorité</b>", "<b>Action Recommandée</b>", "<b>Délai</b>"],
            fill_color=main_color,
            font=dict(color='white', size=16),  # Police augmentée de 14 à 16
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
            font=dict(color='darkblue', size=14),  # Police augmentée de 12 à 14
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

# =====================================================
# FONCTIONS D'AFFICHAGE
# =====================================================

def display_api_status():
    """Affiche le statut de l'API dans la sidebar"""
    health = check_api_health()
    
    if health["status"] == "healthy":
        st.sidebar.success("🟢 API FastAPI Connectée")
        
        # Affichage détaillé si demandé
        if st.sidebar.button("ℹ️ Détails API"):
            st.sidebar.json(health["data"])
            
    elif health["status"] == "offline":
        st.sidebar.error("🔴 API Non Accessible")
        st.sidebar.warning("⚠️ Lancez l'API avec: `docker-compose up`")
        
    else:
        st.sidebar.warning(f"🟡 API: {health['status']}")
        st.sidebar.write(f"Erreur: {health.get('error', 'Inconnue')}")

def display_prediction_result(result: Dict[str, Any]):
    """
    Affiche les résultats de prédiction avec visualisations
    
    Args:
        result: Résultat de la prédiction API
    """
    if not result.get("success"):
        st.error(f"❌ {result.get('error', 'Erreur inconnue')}")
        if result.get('details'):
            st.warning(f"Détails: {result['details']}")
        return
    
    data = result["data"]
    
    # Métriques principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Probabilité Churn",
            f"{data['churn_probability']*100:.1f}%"
        )
    
    with col2:
        prediction_text = "🚨 Churn Prédit" if data['churn_prediction'] == 1 else "✅ Client Stable"
        st.metric(
            "Prédiction",
            prediction_text
        )
    
    with col3:
        st.metric(
            "Confiance", 
            f"{data['confidence_score']*100:.1f}%"
        )
    
    # Niveau de risque avec style
    risk_info = RISK_MESSAGES.get(data['risk_level'], {"emoji": "❓", "color": COLORS["info"]})
    st.markdown(
        f"""
        <div style="background-color: {risk_info['color']}20; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <h3 style="color: {risk_info['color']}; margin: 0;">
                {risk_info['emoji']} {data['risk_level']}
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Recommandation business
    st.info(f"💡 **Recommandation:** {data['business_recommendation']}")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        gauge_fig = create_risk_gauge(
            data['churn_probability'], 
            data['risk_level'],
            data['confidence_score']
        )
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    with col2:
        confidence_fig = create_confidence_bar(data['confidence_score'])
        st.plotly_chart(confidence_fig, use_container_width=True)
    
    # Timeline des recommandations
    timeline_fig = create_recommendation_timeline(
        data['risk_level'], 
        data['business_recommendation']
    )
    st.plotly_chart(timeline_fig, use_container_width=True)

def format_client_data_display(client_data: Dict[str, Any]) -> str:
    """
    Formate les données client pour affichage
    
    Args:
        client_data: Données du client
        
    Returns:
        String formatée
    """
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
# FONCTIONS DE GESTION DES DONNÉES
# =====================================================

def save_prediction_to_history(client_data: Dict[str, Any], prediction: Dict[str, Any]):
    """
    Sauvegarde la prédiction dans l'historique de session
    
    Args:
        client_data: Données du client
        prediction: Résultat de prédiction
    """
    if "prediction_history" not in st.session_state:
        st.session_state.prediction_history = []
    
    history_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "client_data": client_data,
        "prediction": prediction,
        "id": len(st.session_state.prediction_history) + 1
    }
    
    st.session_state.prediction_history.append(history_entry)
    
    # Limiter l'historique à 50 entrées
    if len(st.session_state.prediction_history) > 50:
        st.session_state.prediction_history = st.session_state.prediction_history[-50:]

def get_prediction_history() -> List[Dict[str, Any]]:
    """
    Récupère l'historique des prédictions
    
    Returns:
        Liste des prédictions historiques
    """
    return st.session_state.get("prediction_history", [])

def clear_prediction_history():
    """Vide l'historique des prédictions"""
    st.session_state.prediction_history = []

def export_prediction_history() -> str:
    """
    Exporte l'historique en JSON
    
    Returns:
        String JSON de l'historique
    """
    history = get_prediction_history()
    return json.dumps(history, indent=2, ensure_ascii=False)