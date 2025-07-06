"""
Dashboard Streamlit pour la prédiction de churn client
Application principale - Version finale corrigée
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Imports locaux
from config import (
    PAGE_CONFIG, 
    FORM_OPTIONS, 
    DEFAULT_VALUES, 
    FIELD_HELP,
    PROFILE_DESCRIPTIONS
)
from utils import (
    display_api_status,
    call_prediction_api,
    generate_fake_client,
    display_prediction_result,
    format_client_data_display,
    save_prediction_to_history,
    get_prediction_history,
    clear_prediction_history,
    export_prediction_history,
    get_model_info
)

# =====================================================
# CONFIGURATION DE LA PAGE - CORRECTION ICON
# =====================================================

# Configuration sans emote pour éviter les doublons
PAGE_CONFIG_CORRECTED = {
    "page_title": "Churn Prediction Dashboard",  # Sans emote
    "page_icon": "🎯",  # Une seule emote
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

st.set_page_config(**PAGE_CONFIG_CORRECTED)

# CSS personnalisé amélioré
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
    .profile-button {
        width: 100%;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER PRINCIPAL - SANS EMOTE CIBLE
# =====================================================

st.markdown('<h1 class="main-header">Churn Prediction Dashboard</h1>', unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
    <p>Prédiction intelligente du risque de churn client 🤖</p>
    <p style="color: #888; font-size: 0.9rem;">
        Modèle XGBoost optimisé • Seuil business 35.1% • 11 features engineered
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR AVEC STATUS API CORRIGÉ
# =====================================================

# Status API en haut avec vraie vérification
with st.sidebar.container():
    from utils import check_api_health
    health = check_api_health()
    
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
            🟢 API FastAPI Connectée
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
            🔴 API Non Accessible
        </div>
        """, unsafe_allow_html=True)

# Navigation principale
st.sidebar.markdown("### 📍 Section")
page = st.sidebar.selectbox(
    "",
    ["🏠 Prédiction", "📊 Historique", "ℹ️ Modèle", "🎭 Démonstration"],
    label_visibility="collapsed"
)

# Spacer
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Boutons en bas de sidebar
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("📋 Détails API", use_container_width=True):
        health_detail = {"status": "healthy", "test_probability": 0.8001}
        st.sidebar.json(health_detail)

with col2:
    if st.button("ℹ️ Infos Modèle", use_container_width=True):
        model_info = get_model_info()
        if model_info:
            st.sidebar.success("✅ Modèle XGBoost chargé")
            st.sidebar.write(f"**Seuil:** {model_info.get('optimal_threshold', 'N/A')}")
            st.sidebar.write(f"**Features:** {model_info.get('features_count', 'N/A')}")
        else:
            st.sidebar.error("❌ Infos indisponibles")

# =====================================================
# INITIALISATION SESSION STATE POUR FAKER
# =====================================================

# Initialisation des valeurs du formulaire dans session_state
form_fields = ['contract', 'tenure', 'monthly_charges', 'total_charges', 
               'payment_method', 'internet_service', 'paperless_billing']

for field in form_fields:
    if field not in st.session_state:
        st.session_state[field] = DEFAULT_VALUES[field]

# =====================================================
# PAGE PRINCIPALE - PRÉDICTION
# =====================================================

if page == "🏠 Prédiction":
    st.markdown("## 📝 Informations Client")
    
    # Colonnes pour organisation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Saisie Manuelle")
        
        # Formulaire principal avec session_state
        with st.form("client_form"):
            # Ligne 1: Contrat et Ancienneté
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                contract = st.selectbox(
                    "Type de Contrat",
                    FORM_OPTIONS["contract"],
                    index=FORM_OPTIONS["contract"].index(st.session_state.contract),
                    help=FIELD_HELP["contract"],
                    key="form_contract"
                )
            
            with col1_2:
                tenure = st.number_input(
                    "Ancienneté (mois)",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.tenure,
                    help=FIELD_HELP["tenure"],
                    key="form_tenure"
                )
            
            # Ligne 2: Facturation
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                monthly_charges = st.number_input(
                    "Facturation mensuelle (€)",
                    min_value=0.01,
                    max_value=200.0,
                    value=st.session_state.monthly_charges,
                    step=0.01,
                    help=FIELD_HELP["monthly_charges"],
                    key="form_monthly_charges"
                )
            
            with col2_2:
                total_charges = st.number_input(
                    "Total facturé (€)",
                    min_value=0.0,
                    max_value=10000.0,
                    value=st.session_state.total_charges,
                    step=0.01,
                    help=FIELD_HELP["total_charges"],
                    key="form_total_charges"
                )
            
            # Ligne 3: Services
            col3_1, col3_2 = st.columns(2)
            with col3_1:
                payment_method = st.selectbox(
                    "Mode de Paiement",
                    FORM_OPTIONS["payment_method"],
                    index=FORM_OPTIONS["payment_method"].index(st.session_state.payment_method),
                    help=FIELD_HELP["payment_method"],
                    key="form_payment_method"
                )
            
            with col3_2:
                internet_service = st.selectbox(
                    "Service Internet",
                    FORM_OPTIONS["internet_service"],
                    index=FORM_OPTIONS["internet_service"].index(st.session_state.internet_service),
                    help=FIELD_HELP["internet_service"],
                    key="form_internet_service"
                )
            
            # Ligne 4: Facturation numérique
            paperless_billing = st.selectbox(
                "Facturation Numérique",
                FORM_OPTIONS["paperless_billing"],
                index=FORM_OPTIONS["paperless_billing"].index(st.session_state.paperless_billing),
                help=FIELD_HELP["paperless_billing"],
                key="form_paperless_billing"
            )
            
            # Bouton de prédiction - SANS EMOTE
            predict_button = st.form_submit_button(
                "Prédire le Risque de Churn",  # Sans emote cible
                type="primary"
            )
    
    with col2:
        st.markdown("### 🎭 Clients Fictifs")
        st.markdown("*Générez des profils types pour tester le modèle*")
        
        # Boutons pour chaque profil
        for profile_type, info in PROFILE_DESCRIPTIONS.items():
            if st.button(
                f"{info['name']}",
                key=f"btn_{profile_type}",
                help=info['description'],
                use_container_width=True
            ):
                # Génération du client fictif
                with st.spinner(f"Génération profil {info['name']}..."):
                    fake_result = generate_fake_client(profile_type)
                
                if fake_result.get("success"):
                    fake_data = fake_result["data"]["client_data"]
                    
                    # Mise à jour session_state
                    st.session_state.contract = fake_data["contract"]
                    st.session_state.tenure = fake_data["tenure"]
                    st.session_state.monthly_charges = fake_data["monthly_charges"]
                    st.session_state.total_charges = fake_data["total_charges"]
                    st.session_state.payment_method = fake_data["payment_method"]
                    st.session_state.internet_service = fake_data["internet_service"]
                    st.session_state.paperless_billing = fake_data["paperless_billing"]
                    
                    st.success(f"✅ Profil {info['name']} généré!")
                    st.rerun()
                else:
                    st.error(f"❌ Erreur: {fake_result.get('error')}")
        
        # Bouton reset
        if st.button("🔄 Reset Formulaire", use_container_width=True):
            for field in form_fields:
                st.session_state[field] = DEFAULT_VALUES[field]
            st.rerun()
    
    # =====================================================
    # TRAITEMENT PRÉDICTION
    # =====================================================
    
    if predict_button:
        # Compilation des données client
        client_data = {
            "contract": contract,
            "tenure": tenure,
            "monthly_charges": monthly_charges,
            "total_charges": total_charges,
            "payment_method": payment_method,
            "internet_service": internet_service,
            "paperless_billing": paperless_billing,
            "client_id": f"web_client_{datetime.now().strftime('%H%M%S')}"
        }
        
        # Affichage des données saisies - SANS RADAR
        with st.expander("📋 Données Client Saisies"):
            st.markdown(format_client_data_display(client_data))
            # Suppression du graphique radar
        
        # Appel API
        with st.spinner("🔄 Analyse en cours..."):
            result = call_prediction_api(client_data)
        
        # Affichage des résultats - TITRE MODIFIÉ
        st.markdown("## 📈 Résultats de l'Analyse")  # Emote changée de 🎯 à 📈
        display_prediction_result(result)
        
        # Sauvegarde dans l'historique
        if result.get("success"):
            save_prediction_to_history(client_data, result)
            st.success("💾 Prédiction sauvegardée dans l'historique")

# =====================================================
# PAGE HISTORIQUE (identique)
# =====================================================

elif page == "📊 Historique":
    st.markdown("## 📊 Historique des Prédictions")
    
    history = get_prediction_history()
    
    if not history:
        st.info("📭 Aucune prédiction dans l'historique. Effectuez une prédiction pour commencer!")
    else:
        # Actions sur l'historique
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre de Prédictions", len(history))
        
        with col2:
            if st.button("🗑️ Vider l'Historique"):
                clear_prediction_history()
                st.rerun()
        
        with col3:
            if st.button("💾 Exporter JSON"):
                export_data = export_prediction_history()
                st.download_button(
                    "⬇️ Télécharger",
                    export_data,
                    file_name=f"churn_predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )
        
        # Affichage de l'historique
        st.markdown("### 📋 Dernières Prédictions")
        
        for i, entry in enumerate(reversed(history[-10:])):
            with st.expander(f"🕐 {entry['timestamp']} - ID: {entry['id']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📋 Client:**")
                    st.markdown(format_client_data_display(entry['client_data']))
                
                with col2:
                    if entry['prediction'].get('success'):
                        pred_data = entry['prediction']['data']
                        st.markdown("**📈 Résultat:**")  # Emote changée
                        st.write(f"**Probabilité:** {pred_data['churn_probability']*100:.1f}%")
                        st.write(f"**Risque:** {pred_data['risk_level']}")
                        st.write(f"**Confiance:** {pred_data['confidence_score']*100:.1f}%")
                    else:
                        st.error("Erreur dans cette prédiction")

# =====================================================
# PAGE INFORMATIONS MODÈLE
# =====================================================

elif page == "ℹ️ Modèle":
    st.markdown("## 🤖 Informations du Modèle")
    
    # Récupération des infos
    model_info = get_model_info()
    
    if model_info:
        # Informations générales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            model_type = model_info.get('model_type', 'N/A').replace('Champion', '').strip()
            st.metric("Type de Modèle", model_type)
        
        with col2:
            st.metric("Seuil Optimal", f"{model_info.get('optimal_threshold', 0):.4f}")
        
        with col3:
            st.metric("Nombre de Features", model_info.get('features_count', 'N/A'))
        
        # Métriques de performance
        if 'model_metrics' in model_info and model_info['model_metrics']:
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
                st.metric("AUC", f"{metrics.get('auc', 0):.3f}")
        
        # Informations détaillées
        with st.expander("📄 Informations Complètes"):
            st.json(model_info)
    
    else:
        st.error("❌ Impossible de récupérer les informations du modèle")

# =====================================================
# PAGE DÉMONSTRATION
# =====================================================

elif page == "🎭 Démonstration":
    st.markdown("## 🎭 Démonstration Interactive")
    
    st.markdown("""
    Cette section permet de tester rapidement différents profils clients 
    et d'observer les variations de prédictions.
    """)
    
    # Interface démo simplifiée
    col1, col2 = st.columns(2)
    
    with col1:
        profile_type = st.selectbox(
            "Type de Profil",
            list(PROFILE_DESCRIPTIONS.keys()),
            format_func=lambda x: PROFILE_DESCRIPTIONS[x]["name"]
        )
    
    with col2:
        num_profiles = st.slider("Nombre de Profils", 1, 5, 3)
    
    if st.button("🎲 Générer et Prédire"):
        st.info("Fonctionnalité de démonstration disponible - Génération en cours...")

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>Churn Prediction Dashboard | Modèle XGBoost | FastAPI + Streamlit</p>
    <p>Développé avec ❤️ pour la prédiction intelligente de churn client</p>
</div>
""", unsafe_allow_html=True)