.PHONY: help install dev docker-build docker-up docker-down docker-logs test clean

help:
	@echo "Rowboat API SDK Connector - Makefile"
	@echo "====================================="
	@echo ""
	@echo "Commandes disponibles:"
	@echo "  make install      - Installer les dépendances"
	@echo "  make dev          - Démarrer en mode développement"
	@echo "  make docker-build - Builder l'image Docker"
	@echo "  make docker-up    - Démarrer avec Docker Compose"
	@echo "  make docker-down  - Arrêter les conteneurs Docker"
	@echo "  make docker-logs  - Voir les logs Docker"
	@echo "  make test         - Lancer les tests"
	@echo "  make clean        - Nettoyer les fichiers temporaires"

install:
	@echo "📦 Installation des dépendances..."
	pip install -r requirements.txt

dev:
	@echo "🔧 Démarrage en mode développement..."
	@if [ ! -f .env ]; then \
		echo "⚠️  Fichier .env non trouvé. Copie de .env.example..."; \
		cp .env.example .env; \
		echo "📝 Veuillez éditer .env avec vos credentials"; \
		exit 1; \
	fi
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	@echo "🐳 Building Docker image..."
	docker-compose build

docker-up:
	@echo "🐳 Démarrage des conteneurs Docker..."
	docker-compose up -d
	@echo "✅ Service démarré sur http://localhost:8000"

docker-down:
	@echo "🛑 Arrêt des conteneurs Docker..."
	docker-compose down

docker-logs:
	@echo "📋 Logs Docker..."
	docker-compose logs -f

test:
	@echo "🧪 Lancement des tests..."
	@echo "TODO: Ajouter les tests"

clean:
	@echo "🧹 Nettoyage..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Nettoyage terminé"
