#!/bin/bash

# Script pour démarrer le service Rowboat API SDK Connector

set -e

echo "🚀 Rowboat API SDK Connector - Startup Script"
echo "=============================================="

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env non trouvé. Création depuis .env.example..."
    cp .env.example .env
    echo "📝 Veuillez éditer le fichier .env avec vos credentials Rowboat"
    echo "   - ROWBOAT_HOST"
    echo "   - ROWBOAT_API_KEY"
    echo "   - ROWBOAT_PROJECT_ID"
    exit 1
fi

# Vérifier que les variables essentielles sont définies
source .env

if [ -z "$ROWBOAT_API_KEY" ] || [ -z "$ROWBOAT_PROJECT_ID" ]; then
    echo "❌ Erreur: ROWBOAT_API_KEY et ROWBOAT_PROJECT_ID doivent être définis dans .env"
    exit 1
fi

echo "✅ Configuration chargée"
echo "   Host: ${ROWBOAT_HOST}"
echo "   Project ID: ${ROWBOAT_PROJECT_ID}"
echo "   Debug: ${DEBUG:-false}"

# Choisir le mode de démarrage
if [ "$1" == "dev" ]; then
    echo ""
    echo "🔧 Mode développement"
    echo "   Installation des dépendances..."
    pip install -r requirements.txt

    echo "   Démarrage du serveur avec hot-reload..."
    python -m uvicorn app.main:app --reload --host ${HOST:-0.0.0.0} --port ${PORT:-8000}

elif [ "$1" == "docker" ]; then
    echo ""
    echo "🐳 Mode Docker"
    echo "   Building and starting containers..."
    docker-compose up --build

elif [ "$1" == "prod" ]; then
    echo ""
    echo "🚀 Mode production"
    echo "   Installation des dépendances..."
    pip install -r requirements.txt

    echo "   Démarrage du serveur..."
    python -m uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --workers 4

else
    echo ""
    echo "Usage: ./run.sh [mode]"
    echo ""
    echo "Modes disponibles:"
    echo "  dev     - Mode développement avec hot-reload"
    echo "  docker  - Démarrage avec Docker Compose"
    echo "  prod    - Mode production avec workers multiples"
    echo ""
    echo "Exemple: ./run.sh dev"
    exit 1
fi
