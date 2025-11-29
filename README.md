# Rowboat API SDK Connector

Un webservice headless **stateless** pour Rowboat SDK avec support OpenWebUI. Les credentials Rowboat sont passés dynamiquement dans chaque requête, permettant d'utiliser le service avec plusieurs projets Rowboat.

## Fonctionnalités

- **API REST stateless** - Aucune configuration Rowboat au démarrage
- **Multi-projets** - Utilisez plusieurs projets Rowboat avec un seul service
- **Support OpenWebUI** avec endpoint dédié (`/owui`)
- **Mode debug** pour diagnostic détaillé
- **Gestion de conversations** avec support de `conversation_id`
- **Déploiement facile** via Docker
- **Compatible** avec Dokploy, Coolify, et Kubero

## Architecture

Ce webservice fonctionne en mode **stateless** :
- **Pas de configuration Rowboat au démarrage**
- Les credentials (HOST, API_KEY, PROJECT_ID) sont passés **dans chaque requête**
- Permet d'utiliser dynamiquement plusieurs projets Rowboat
- Parfait pour l'intégration avec OpenWebUI

## Installation Locale

### 1. Cloner le repository

```bash
git clone <votre-repo>
cd rowboat-api-sdk-connector
```

### 2. Configurer (optionnel)

```bash
cp .env.example .env
```

Éditez `.env` pour la configuration du serveur uniquement :

```env
PORT=8000
HOST=0.0.0.0
DEBUG=false
ENABLE_OWUI=true
```

**Note** : Les credentials Rowboat ne sont PAS configurés ici. Ils sont passés dans chaque requête.

### 3. Démarrer avec Docker Compose

```bash
docker-compose up -d
```

Le service sera accessible sur `http://localhost:8000`

### 4. Vérifier le déploiement

```bash
curl http://localhost:8000/health
```

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

Récupère la configuration du service.

**Réponse :**
```json
{
  "mode": "stateless",
  "credentials_required_per_request": true,
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
  "credentials": {
    "host": "https://app.rowboatlabs.com",
    "api_key": "your_api_key",
    "project_id": "your_project_id"
  },
  "messages": [
    {
      "role": "user",
      "content": "Quelle est la capitale de la France ?"
    }
  ],
  "conversation_id": null,
  "mock_tools": null
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

### POST `/owui` (OpenWebUI)

Endpoint spécifique pour l'intégration avec OpenWebUI.

**Requête :**
```json
{
  "credentials": {
    "host": "https://app.rowboatlabs.com",
    "api_key": "your_api_key",
    "project_id": "your_project_id"
  },
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

### Fonction OpenWebUI Complète

Copiez le code de `examples/openwebui_function.py` dans OpenWebUI. Voici un exemple simplifié :

```python
import requests

# Configuration
ROWBOAT_SERVICE_URL = "http://your-service:8000/owui"
ROWBOAT_HOST = "https://app.rowboatlabs.com"
ROWBOAT_API_KEY = "your_api_key"
ROWBOAT_PROJECT_ID = "your_project_id"

def rowboat_chat(messages, debug=False):
    """
    Fonction Rowboat pour OpenWebUI
    """
    payload = {
        "credentials": {
            "host": ROWBOAT_HOST,
            "api_key": ROWBOAT_API_KEY,
            "project_id": ROWBOAT_PROJECT_ID
        },
        "messages": messages,
        "debug": debug
    }

    response = requests.post(ROWBOAT_SERVICE_URL, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()

    if debug and "metadata" in result:
        print(f"DEBUG: {result['metadata']}")

    return result["response"]
```

### Utilisation dans OpenWebUI

```python
# Exemple d'utilisation
messages = [
    {"role": "user", "content": "Bonjour"}
]

response = rowboat_chat(messages, debug=True)
print(response)
```

## Exemples d'Utilisation

### Exemple 1 : Conversation Simple avec curl

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "host": "https://app.rowboatlabs.com",
      "api_key": "your_api_key",
      "project_id": "your_project_id"
    },
    "messages": [
      {"role": "user", "content": "Quelle est la capitale de la France ?"}
    ]
  }'
```

### Exemple 2 : Avec Python

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "credentials": {
            "host": "https://app.rowboatlabs.com",
            "api_key": "your_api_key",
            "project_id": "your_project_id"
        },
        "messages": [
            {"role": "user", "content": "Bonjour"}
        ]
    }
)

result = response.json()
print(result["response"])
print(f"Conversation ID: {result['conversation_id']}")
```

### Exemple 3 : Multi-projets

Le même service peut gérer plusieurs projets :

```python
# Projet 1
response1 = requests.post(url, json={
    "credentials": {
        "host": "https://app.rowboatlabs.com",
        "api_key": "key_project_1",
        "project_id": "project_1"
    },
    "messages": [{"role": "user", "content": "Hello"}]
})

# Projet 2 avec le même service
response2 = requests.post(url, json={
    "credentials": {
        "host": "https://app.rowboatlabs.com",
        "api_key": "key_project_2",
        "project_id": "project_2"
    },
    "messages": [{"role": "user", "content": "Bonjour"}]
})
```

## Mode Debug

Activez le debug par requête avec `"debug": true` :

```bash
curl -X POST http://localhost:8000/owui \
  -H "Content-Type: application/json" \
  -d '{
    "credentials": {
      "host": "https://app.rowboatlabs.com",
      "api_key": "your_key",
      "project_id": "your_project_id"
    },
    "messages": [{"role": "user", "content": "Test"}],
    "debug": true
  }'
```

Le mode debug fournira :
- Configuration Rowboat utilisée
- Nombre de messages traités
- Informations détaillées de la conversation
- Logs dans les sorties du conteneur

## Déploiement

### Docker Compose (Local)

```bash
docker-compose up -d
```

### Dokploy

1. Importez le repository dans Dokploy
2. Dokploy détectera automatiquement `dokploy.json`
3. Aucune variable d'environnement Rowboat requise !
4. Déployez

### Coolify

1. Créez une application dans Coolify
2. Sélectionnez le repository
3. Coolify détectera `coolify.json`
4. Déployez

### Kubero

1. Créez une app dans Kubero
2. Kubero utilisera `app.yaml`
3. Déployez

## Structure du Projet

```
rowboat-api-sdk-connector/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI
│   ├── config.py            # Configuration
│   ├── models.py            # Modèles Pydantic
│   └── rowboat_service.py   # Service Rowboat (stateless)
├── examples/
│   ├── openwebui_function.py  # Fonction OpenWebUI
│   └── test_api.py            # Tests API
├── Dockerfile
├── docker-compose.yml
├── dokploy.json
├── coolify.json
├── app.yaml
├── requirements.txt
└── README.md
```

## Développement Local

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
./run.sh dev
# ou
make dev
```

## Avantages du Mode Stateless

1. **Multi-projets** : Un seul service pour tous vos projets Rowboat
2. **Sécurité** : Pas de credentials stockés dans le service
3. **Flexibilité** : Changez de projet par requête
4. **Simplicité** : Aucune configuration au démarrage

## Tests

Utilisez le script de test fourni :

```bash
python examples/test_api.py
```

**Note** : Configurez les credentials dans le script avant de tester.

## Sécurité

- Ne jamais exposer vos API keys dans le code
- Utilisez HTTPS en production
- Limitez l'accès au service avec un firewall
- Considérez l'ajout d'authentification au service

## Support

Pour toute question :
1. Consultez la documentation Rowboat : https://docs.rowboatlabs.com
2. Vérifiez les logs : `docker-compose logs -f`
3. Testez avec le mode debug activé

## License

MIT
