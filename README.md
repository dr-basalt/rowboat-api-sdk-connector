# Rowboat API SDK Connector

Un webservice headless pour Rowboat SDK avec support OpenWebUI, déployable sur Dokploy, Coolify, et Kubero.

## Fonctionnalités

- **API REST complète** pour interagir avec Rowboat SDK
- **Support OpenWebUI** avec endpoint dédié (`/owui`)
- **Mode debug** pour diagnostic détaillé
- **Gestion de conversations** avec support de `conversation_id`
- **Déploiement facile** via Docker
- **Compatible** avec Dokploy, Coolify, et Kubero
- **Health checks** intégrés

## Prérequis

- Docker et Docker Compose (pour déploiement local)
- Un compte Rowboat avec :
  - `API_KEY`
  - `PROJECT_ID`
  - `HOST` (https://app.rowboatlabs.com ou votre instance)

## Installation Locale

### 1. Cloner le repository

```bash
git clone <votre-repo>
cd rowboat-api-sdk-connector
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Éditez le fichier `.env` avec vos credentials Rowboat :

```env
ROWBOAT_HOST=https://app.rowboatlabs.com
ROWBOAT_API_KEY=votre_api_key
ROWBOAT_PROJECT_ID=votre_project_id
DEBUG=false
ENABLE_OWUI=true
```

### 3. Démarrer avec Docker Compose

```bash
docker-compose up -d
```

Le service sera accessible sur `http://localhost:8000`

### 4. Vérifier le déploiement

```bash
curl http://localhost:8000/health
```

## Déploiement sur Plateformes Cloud

### Dokploy

1. Importez le repository dans Dokploy
2. Dokploy détectera automatiquement le fichier `dokploy.json`
3. Configurez les variables d'environnement dans l'interface :
   - `ROWBOAT_API_KEY`
   - `ROWBOAT_PROJECT_ID`
   - `ROWBOAT_HOST` (optionnel, défaut: https://app.rowboatlabs.com)
4. Déployez l'application

### Coolify

1. Créez une nouvelle application dans Coolify
2. Sélectionnez le repository
3. Coolify détectera le fichier `coolify.json`
4. Configurez les variables d'environnement sensibles :
   - `ROWBOAT_API_KEY`
   - `ROWBOAT_PROJECT_ID`
5. Déployez

### Kubero

1. Créez une nouvelle app dans Kubero
2. Kubero utilisera le fichier `app.yaml`
3. Dans l'interface Kubero, configurez :
   - `ROWBOAT_API_KEY`
   - `ROWBOAT_PROJECT_ID`
4. Déployez l'application

## API Endpoints

### GET `/health`

Vérification de l'état du service.

**Réponse :**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "rowboat_configured": true
}
```

### GET `/config`

Récupère la configuration actuelle (sans informations sensibles).

**Réponse :**
```json
{
  "rowboat_host": "https://app.rowboatlabs.com",
  "project_id": "your_project_id",
  "debug": false,
  "enable_owui": true,
  "version": "0.1.0"
}
```

### POST `/chat`

Endpoint principal pour interagir avec Rowboat.

**Requête :**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Quelle est la capitale de la France ?"
    }
  ],
  "conversation_id": null,
  "mock_tools": null,
  "stream": false
}
```

**Réponse :**
```json
{
  "response": "La capitale de la France est Paris.",
  "conversation_id": "conv_123abc",
  "debug_info": null
}
```

**Continuer une conversation :**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Quelle est sa population ?"
    }
  ],
  "conversation_id": "conv_123abc"
}
```

### POST `/owui` (OpenWebUI)

Endpoint spécifique pour l'intégration avec OpenWebUI.

**Requête :**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Bonjour"
    }
  ],
  "conversation_id": null,
  "debug": true
}
```

**Réponse :**
```json
{
  "response": "Bonjour ! Comment puis-je vous aider ?",
  "conversation_id": "conv_456def",
  "metadata": {
    "conversation_id": "conv_456def",
    "service_version": "0.1.0",
    "debug": {
      "rowboat_host": "https://app.rowboatlabs.com",
      "project_id": "your_project_id",
      "messages_count": 1
    }
  }
}
```

## Intégration avec OpenWebUI

### Méthode 1 : Function Tool

Créez une nouvelle fonction dans OpenWebUI :

```python
import requests
import json

def rowboat_chat(messages: list, debug: bool = False) -> str:
    """
    Fonction Rowboat pour OpenWebUI

    :param messages: Liste des messages de la conversation
    :param debug: Active le mode debug pour plus d'informations
    :return: Réponse de l'assistant
    """

    # URL de votre service Rowboat
    url = "http://your-service-url:8000/owui"

    # Préparer les messages au format attendu
    formatted_messages = [
        {"role": msg.get("role", "user"), "content": msg.get("content", "")}
        for msg in messages
    ]

    payload = {
        "messages": formatted_messages,
        "debug": debug
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Afficher les infos de debug si demandé
        if debug and "metadata" in result and "debug" in result["metadata"]:
            print(f"DEBUG INFO: {json.dumps(result['metadata']['debug'], indent=2)}")

        return result["response"]

    except Exception as e:
        return f"Erreur lors de l'appel à Rowboat: {str(e)}"
```

### Méthode 2 : API directe

Vous pouvez également appeler directement l'API depuis n'importe quelle application :

```python
import requests

response = requests.post(
    "http://your-service-url:8000/chat",
    json={
        "messages": [
            {"role": "user", "content": "Bonjour"}
        ]
    }
)

result = response.json()
print(result["response"])
print(f"Conversation ID: {result['conversation_id']}")
```

## Mode Debug

Pour activer le mode debug globalement, configurez `DEBUG=true` dans vos variables d'environnement.

Pour activer le debug par requête (endpoint `/owui`), passez `"debug": true` dans la requête :

```bash
curl -X POST http://localhost:8000/owui \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Test"}],
    "debug": true
  }'
```

Le mode debug fournira :
- Nombre de messages traités
- Informations sur la conversation
- Configuration Rowboat utilisée
- Logs détaillés dans les sorties du conteneur

## Exemples d'Utilisation

### Exemple 1 : Conversation Simple

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Quelle est la capitale de la France ?"}
    ]
  }'
```

### Exemple 2 : Continuation de Conversation

```bash
# Première requête
CONV_ID=$(curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Quelle est la capitale de la France ?"}
    ]
  }' | jq -r '.conversation_id')

# Deuxième requête avec le même conversation_id
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"messages\": [
      {\"role\": \"user\", \"content\": \"Quelle est sa population ?\"}
    ],
    \"conversation_id\": \"$CONV_ID\"
  }"
```

### Exemple 3 : Mock Tools (Test)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Quel temps fait-il ?"}
    ],
    "mock_tools": {
      "weather_lookup": "Il fait beau et 25°C partout."
    }
  }'
```

## Logs et Monitoring

### Voir les logs en temps réel

```bash
docker-compose logs -f rowboat-connector
```

### Vérifier les métriques

Le service expose un endpoint de health check qui peut être utilisé pour le monitoring :

```bash
curl http://localhost:8000/health
```

## Dépannage

### Le service ne démarre pas

1. Vérifiez que toutes les variables d'environnement sont configurées :
   ```bash
   docker-compose config
   ```

2. Vérifiez les logs :
   ```bash
   docker-compose logs rowboat-connector
   ```

### Erreur 503 "Rowboat service not initialized"

Cela signifie que le service Rowboat n'a pas pu s'initialiser. Vérifiez :
- Que `ROWBOAT_API_KEY` est défini et valide
- Que `ROWBOAT_PROJECT_ID` est défini et valide
- Que `ROWBOAT_HOST` est accessible

### Erreur lors de l'appel à Rowboat

Vérifiez :
1. Que votre projet est déployé en production dans Rowboat Studio
2. Que l'API key a les permissions nécessaires
3. Les logs du service pour plus de détails

## Développement

### Installation locale pour développement

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos credentials

# Lancer le serveur en mode développement
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Structure du Projet

```
rowboat-api-sdk-connector/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI principale
│   ├── config.py            # Configuration et settings
│   ├── models.py            # Modèles Pydantic
│   └── rowboat_service.py   # Service Rowboat
├── Dockerfile
├── docker-compose.yml
├── dokploy.json            # Configuration Dokploy
├── coolify.json            # Configuration Coolify
├── app.yaml                # Configuration Kubero
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Sécurité

- Ne jamais committer le fichier `.env` avec vos credentials
- Utilisez des secrets managers pour les déploiements en production
- Limitez l'accès à l'API avec un reverse proxy et authentification si nécessaire
- Activez HTTPS en production

## License

MIT

## Support

Pour toute question ou problème :
1. Vérifiez la documentation Rowboat : https://docs.rowboatlabs.com
2. Consultez les logs du service
3. Créez une issue sur le repository

## Roadmap

- [ ] Support du streaming pour les réponses
- [ ] Authentification JWT
- [ ] Rate limiting
- [ ] Métriques Prometheus
- [ ] Support multi-projets
- [ ] Interface web d'administration
