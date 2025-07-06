# =====================================================
# Image de base Python 3.11
# =====================================================
FROM python:3.11-slim

# Variables d'environnement pour production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Création utilisateur non-root pour sécurité
RUN groupadd -r churn && useradd -r -g churn churn

# Répertoire de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY --chown=churn:churn . .

# Changement vers utilisateur non-root
USER churn

# Port exposé
EXPOSE $PORT

# Health check simplifié
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Commande de démarrage
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]