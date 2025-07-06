# 🎯 Churn Prediction ML Portfolio

> **Service de prédiction de churn client avec architecture production complète**  
> *Machine Learning • FastAPI • Docker • Streamlit Cloud • XGBoost*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.0+-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 **Démonstration Live**

### 🌐 **Version Cloud (Accessible Publiquement)**
**[🎯 Churn Prediction Dashboard](https://churn-prediction-xgboost.streamlit.app/)**

### 💻 **Version Technique Complète**
```bash
git clone https://github.com/EP-portfolio/churn-prediction.git
cd churn-prediction
docker-compose up
# → http://localhost:8501 (Dashboard) + http://localhost:8000 (API)
```

---

## 📊 **Performance du Modèle**

| Métrique           | Valeur | Objectif | Status                 |
| ------------------ | ------ | -------- | ---------------------- |
| **Recall**         | 88.5%  | >80%     | ✅ **Dépassé**          |
| **Precision**      | 65.2%  | -        | ✅ **Optimisé**         |
| **Business Score** | 0.8426 | -        | ✅ **ROI Optimisé**     |
| **AUC**            | 0.851  | >0.8     | ✅ **Excellent**        |
| **Seuil Optimal**  | 35.1%  | -        | 🎯 **Calibré Business** |

**🎯 Seuil optimisé selon les coûts réels :** *Acquisition client = 5x coût rétention*

---

## 🏗️ **Architecture Technique**

### **🔄 Dual Architecture Approach**

```
Data Science Notebook → Pipeline ML Industrialisé → Architecture Choice
                                                   ↓
                                     ┌─────────────────────────────┐
                                     │                             │
                               Production                      Cloud Demo
                                     │                             │
                         FastAPI + Docker + Streamlit    Streamlit Cloud Unified
                                     │                             │
                              Microservices                 Public URL Demo
                              API Documentation           Instant Deployment
                              Container Orchestration     Portfolio Showcase
```

### **🎯 Version 1 : Architecture Microservices**
```
┌─────────────────┐    HTTP     ┌──────────────────┐
│   STREAMLIT     │──────────→  │   API FASTAPI    │
│   localhost:8501│             │   localhost:8000 │
│                 │             │                  │
│ • Interface     │             │ • XGBoost Model  │
│ • Visualizations│             │ • 11 Features    │
│ • User Forms    │             │ • Business Logic │
└─────────────────┘             └──────────────────┘
            │                            │
            └──────────── DOCKER ────────┘
```

### **☁️ Version 2 : Streamlit Cloud Unified**
```
┌─────────────────────────────────────────┐
│        STREAMLIT CLOUD APP              │
│                                         │
│  🎨 Interface + 🧠 ML Pipeline          │
│  🎭 Faker + 📊 Visualizations          │
│  📈 Business Logic + 💾 History        │
└─────────────────────────────────────────┘
```

---

## 🛠️ **Stack Technique**

### **🎯 Machine Learning**
- **Modèle** : XGBoost Champion avec hyperparamètres optimisés
- **Features** : 11 features engineered (à partir de 7 features business)
- **Pipeline** : Preprocessing automatisé + validation Pydantic
- **Persistence** : Joblib + LabelEncoders sauvegardés

### **🚀 Backend & API**
- **FastAPI** : API REST avec documentation Swagger automatique
- **Docker** : Containerisation complète avec docker-compose
- **Validation** : Pydantic pour validation robuste des inputs
- **Logging** : Structured logging pour monitoring

### **🎨 Frontend & UX**
- **Streamlit** : Interface interactive avec cache optimisé
- **Plotly** : Visualisations interactives (gauge, graphiques)
- **Faker** : Génération de 5 profils clients types
- **Export** : Historique des prédictions en JSON

### **📊 Data & Features**
```python
# 7 Features Business → 11 Features Engineered
'contract', 'tenure', 'monthly_charges', 'total_charges',
'payment_method', 'internet_service', 'paperless_billing'
↓
'Ratio_MonthlyCharges_tenure', 'Contract', 'tenure', 
'MonthlyCharges', 'tenure_segment_encoded', 'TotalCharges',
'is_new_customer', 'PaymentMethod', 'InternetService', 
'PaperlessBilling', 'Ratio_TotalCharges_MonthlyCharges*tenure'
```

---

## 🎭 **Fonctionnalités**

### **🤖 Intelligence Métier**
- ✅ **Prédiction temps réel** avec seuil business optimisé
- ✅ **Recommandations automatiques** selon le niveau de risque
- ✅ **Score de confiance** basé sur la distance au seuil
- ✅ **Interprétation business** : 6 niveaux de risque détaillés

### **🎮 Interface Utilisateur**
- ✅ **Formulaires intuitifs** avec validation temps réel
- ✅ **Génération clients fictifs** : 5 profils (Aléatoire, Haut Risque, Stable, Nouveau, Premium)
- ✅ **Visualisations interactives** : Gauge de risque, graphiques de confiance
- ✅ **Timeline d'actions** : Plan recommandé selon le risque
- ✅ **Historique session** : Sauvegarde et export des prédictions

### **📊 Monitoring & Observabilité**
- ✅ **Health checks** automatiques du modèle
- ✅ **Métriques de performance** en temps réel  
- ✅ **Logging structuré** pour debugging
- ✅ **Tests de régression** sur données de référence

---

## 🚀 **Quick Start**

### **⚡ Version Cloud (Recommandée)**
```bash
# Accès direct - Aucune installation requise
→ https://churn-prediction-xgboost.streamlit.app/
```

### **🐳 Version Docker (Architecture Complète)**
```bash
# 1. Clone du repository
git clone https://github.com/EP-portfolio/churn-prediction.git
cd churn-prediction

# 2. Lancement avec Docker
docker-compose up

# 3. Accès aux services
# → Dashboard: http://localhost:8501
# → API Docs: http://localhost:8000/docs
# → Health: http://localhost:8000/health
```

### **🔧 Installation Manuelle**
```bash
# 1. Environnement Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 2. Installation dépendances
pip install -r requirements.txt

# 3. Lancement API (terminal 1)
cd api
uvicorn main:app --reload

# 4. Lancement Dashboard (terminal 2)  
cd streamlit_app
streamlit run app.py
```

---

## 📁 **Structure du Projet**

```
churn-prediction/
├── 📄 README.md                    ← Ce fichier
├── 🐳 docker-compose.yml           ← Orchestration complète
├── 📋 requirements.txt             ← Dépendances principales
├── 🏗️ architecture_complete/       ← Version microservices
│   ├── 🚀 api/                    ← FastAPI backend
│   ├── 🎨 streamlit_app/          ← Interface locale
│   └── 📖 README.md               ← Documentation technique
├── ☁️ streamlit_cloud/             ← Version déployable
│   ├── 🎯 app.py                  ← Application unifiée
│   ├── 📦 requirements.txt        ← Dépendances cloud
│   └── 🌐 README.md               ← Guide déploiement
├── 🧠 src/                        ← Pipeline ML
│   ├── 🔧 preprocessing.py        ← Feature engineering
│   ├── 🎯 model_wrapper.py        ← Wrapper intelligent
│   ├── 📊 encoders.py             ← Gestion encoders
│   └── ⚙️ feature_engineering.py  ← Features dérivées
├── 📊 models_production/          ← Artefacts modèle
├── 🏷️ encoders_churn/            ← Encoders LabelEncoder
├── ⚙️ config/                     ← Configuration centralisée
├── 🧪 tests/                      ← Tests automatisés
└── 📚 docs/                       ← Documentation
    ├── 🏗️ ARCHITECTURE.md         ← Design technique
    ├── 🚀 DEPLOYMENT.md            ← Guide déploiement
    └── 📊 API_DOCS.md              ← Documentation API
```

---

## 🧪 **Tests & Validation**

### **✅ Pipeline de Tests**
```bash
# Tests unitaires
pytest tests/

# Validation modèle
python tests/test_model_performance.py

# Tests API
python tests/test_api_endpoints.py

# Tests preprocessing
python tests/test_feature_engineering.py
```

### **📊 Métriques de Qualité**
- ✅ **Code Coverage** : >85%
- ✅ **Tests unitaires** : 100% modules critiques
- ✅ **Validation croisée** : 5-fold CV stable
- ✅ **Reproductibilité** : Seeds fixés, résultats déterministes

---

## 🎯 **Business Impact**

### **💰 ROI Calculé**
```python
# Hypothèses business
cout_acquisition_client = 500€
cout_retention_client = 100€
taux_churn_baseline = 25%

# Impact modèle (seuil 35.1%)
clients_detectes = 88.5%  # Recall
reduction_churn = 15%     # Estimation conservative

# → Économies estimées : 65€ par client traité
```

### **🎯 Cas d'Usage**
1. **Détection précoce** : Identification clients à risque
2. **Actions personnalisées** : Recommandations selon le profil
3. **Optimisation budget** : Focus sur clients récupérables
4. **Monitoring continu** : Surveillance évolution risque

---

## 📈 **Roadmap & Évolutions**

### **🔄 Version 2.0 (WIP)**
- [ ] **MLOps Pipeline** : CI/CD avec MLflow + DVC
- [ ] **Monitoring Avancé** : Drift detection + alertes
- [ ] **APIs Étendues** : Prédictions batch + webhooks
- [ ] **Dashboard Admin** : Gestion modèles + métriques
- [ ] **Intégration CRM** : Connecteurs Salesforce/HubSpot

### **🎯 Améliorations Techniques (WIP)**
- [ ] **Modèles Ensemble** : Stacking XGBoost + LightGBM
- [ ] **Feature Store** : Centralisation features temps réel
- [ ] **A/B Testing** : Framework expérimentation modèles
- [ ] **Scalabilité** : Kubernetes + auto-scaling

---

## 🤝 **Contribution & Développement**

### **🛠️ Setup Développeur**
```bash
# 1. Fork et clone
git clone https://github.com/EP-portfolio/churn-prediction.git

# 2. Installation environnement dev
make setup-dev

# 3. Tests avant commit
make test-all

# 4. Commit avec hooks pre-commit
git commit -m "feat: nouvelle fonctionnalité"
```

### **📋 Standards Qualité**
- ✅ **Black** : Formatage code automatique
- ✅ **Flake8** : Linting et standards PEP8
- ✅ **MyPy** : Type checking statique
- ✅ **Pre-commit** : Hooks qualité automatiques

---

## 📞 **Contact & Portfolio**

### **👨‍💻 Développeur**
- **GitHub** : [@EP-portfolio](https://github.com/EP-portfolio)
- **LinkedIn** : [Eddy Ponton](https://linkedin.com/in/eddy-ponton-0916aa303)
- 

### **🔗 Projets Connexes**
- **📊 Portfolio Data Science** : [Repository ML Projects](https://github.com/EP-portfolio)

---

## 📜 **Licence**

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---


### 🎯 **Prédiction Intelligente • Architecture Scalable • Impact Business**

**Développé avec ❤️ pour démontrer l'excellence en Data Science et Engineering**

[⭐ Star ce repo](https://github.com/EP-portfolio/churn-prediction) • [🐛 Reporter un bug](https://github.com/EP-portfolio/churn-prediction/issues) • [💡 Suggérer une amélioration](https://github.com/EP-portfolio/churn-prediction/discussions)

