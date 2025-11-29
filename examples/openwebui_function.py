"""
Example OpenWebUI Function for Rowboat API SDK Connector

Copy this code into OpenWebUI as a custom function to integrate with Rowboat.
"""

import requests
import json
from typing import List, Dict, Optional


# Configuration - À modifier selon votre déploiement
ROWBOAT_SERVICE_URL = "http://localhost:8000/owui"

# Configuration Rowboat - À modifier avec vos credentials
ROWBOAT_HOST = "https://app.rowboatlabs.com"
ROWBOAT_API_KEY = "your_api_key_here"
ROWBOAT_PROJECT_ID = "your_project_id_here"


def rowboat_chat(
    messages: List[Dict[str, str]],
    rowboat_host: str = ROWBOAT_HOST,
    rowboat_api_key: str = ROWBOAT_API_KEY,
    rowboat_project_id: str = ROWBOAT_PROJECT_ID,
    conversation_id: Optional[str] = None,
    debug: bool = False
) -> str:
    """
    Fonction Rowboat pour OpenWebUI

    Cette fonction permet d'utiliser Rowboat dans OpenWebUI de manière headless.
    Les credentials Rowboat sont passés dynamiquement à chaque requête.

    Args:
        messages: Liste des messages de la conversation
                 Format: [{"role": "user/assistant/system", "content": "..."}]
        rowboat_host: URL du serveur Rowboat (ex: https://app.rowboatlabs.com)
        rowboat_api_key: Clé API Rowboat
        rowboat_project_id: ID du projet Rowboat
        conversation_id: ID de conversation optionnel pour continuer une conversation
        debug: Active le mode debug pour afficher des informations détaillées

    Returns:
        str: La réponse de l'assistant Rowboat

    Examples:
        >>> messages = [{"role": "user", "content": "Bonjour"}]
        >>> response = rowboat_chat(
        ...     messages,
        ...     rowboat_host="https://app.rowboatlabs.com",
        ...     rowboat_api_key="your_key",
        ...     rowboat_project_id="your_project_id",
        ...     debug=True
        ... )
        >>> print(response)
    """

    try:
        # Préparer le payload avec credentials
        payload = {
            "credentials": {
                "host": rowboat_host,
                "api_key": rowboat_api_key,
                "project_id": rowboat_project_id
            },
            "messages": messages,
            "debug": debug
        }

        # Ajouter conversation_id si fourni
        if conversation_id:
            payload["conversation_id"] = conversation_id

        # Faire la requête
        response = requests.post(
            ROWBOAT_SERVICE_URL,
            json=payload,
            timeout=60  # Timeout de 60 secondes
        )

        # Vérifier le statut
        response.raise_for_status()

        # Parser la réponse
        result = response.json()

        # Afficher les informations de debug si demandé
        if debug:
            print("\n" + "="*50)
            print("DEBUG INFORMATION")
            print("="*50)

            if "metadata" in result:
                print(f"\n📋 Metadata:")
                print(json.dumps(result["metadata"], indent=2))

            if "conversation_id" in result:
                print(f"\n💬 Conversation ID: {result['conversation_id']}")

            print("="*50 + "\n")

        # Retourner la réponse
        return result.get("response", "Aucune réponse reçue")

    except requests.exceptions.Timeout:
        error_msg = "⏱️ Timeout: Le service Rowboat n'a pas répondu à temps"
        print(error_msg)
        return error_msg

    except requests.exceptions.ConnectionError:
        error_msg = f"🔌 Erreur de connexion: Impossible de contacter {ROWBOAT_SERVICE_URL}"
        print(error_msg)
        return error_msg

    except requests.exceptions.HTTPError as e:
        error_msg = f"❌ Erreur HTTP {e.response.status_code}: {e.response.text}"
        print(error_msg)
        return error_msg

    except Exception as e:
        error_msg = f"❌ Erreur inattendue: {str(e)}"
        print(error_msg)
        return error_msg


# Fonction alternative avec gestion de l'état de conversation
class RowboatConversation:
    """
    Classe pour gérer une conversation Rowboat avec état.

    Usage dans OpenWebUI:
        conv = RowboatConversation(
            host="https://app.rowboatlabs.com",
            api_key="your_key",
            project_id="your_project_id",
            debug=True
        )
        response1 = conv.send("Bonjour")
        response2 = conv.send("Comment ça va ?")  # Continue la même conversation
    """

    def __init__(
        self,
        host: str = ROWBOAT_HOST,
        api_key: str = ROWBOAT_API_KEY,
        project_id: str = ROWBOAT_PROJECT_ID,
        debug: bool = False
    ):
        """
        Initialise une nouvelle conversation.

        Args:
            host: URL du serveur Rowboat
            api_key: Clé API Rowboat
            project_id: ID du projet Rowboat
            debug: Active le mode debug
        """
        self.host = host
        self.api_key = api_key
        self.project_id = project_id
        self.conversation_id = None
        self.debug = debug
        self.history = []

    def send(self, message: str, role: str = "user") -> str:
        """
        Envoie un message et retourne la réponse.

        Args:
            message: Le message à envoyer
            role: Le rôle du message (user, assistant, system)

        Returns:
            str: La réponse de l'assistant
        """
        # Ajouter le message à l'historique
        self.history.append({"role": role, "content": message})

        # Envoyer à Rowboat
        response = rowboat_chat(
            messages=self.history,
            rowboat_host=self.host,
            rowboat_api_key=self.api_key,
            rowboat_project_id=self.project_id,
            conversation_id=self.conversation_id,
            debug=self.debug
        )

        # Mettre à jour l'historique avec la réponse
        self.history.append({"role": "assistant", "content": response})

        return response

    def reset(self):
        """Réinitialise la conversation."""
        self.conversation_id = None
        self.history = []


# Test de la fonction (à exécuter uniquement pour tester)
if __name__ == "__main__":
    print("🧪 Test de la fonction Rowboat pour OpenWebUI\n")

    # Vérifier que les credentials sont configurés
    if ROWBOAT_API_KEY == "your_api_key_here":
        print("⚠️  ATTENTION: Configurez vos credentials Rowboat avant de tester!")
        print("   Modifiez les constantes ROWBOAT_HOST, ROWBOAT_API_KEY et ROWBOAT_PROJECT_ID\n")
        exit(1)

    # Test 1: Simple message
    print("Test 1: Message simple")
    print("-" * 50)
    messages = [
        {"role": "user", "content": "Bonjour, qui es-tu ?"}
    ]
    response = rowboat_chat(messages, debug=True)
    print(f"Réponse: {response}\n")

    # Test 2: Conversation avec état
    print("\nTest 2: Conversation avec état")
    print("-" * 50)
    conv = RowboatConversation(debug=True)

    print("User: Quelle est la capitale de la France ?")
    response1 = conv.send("Quelle est la capitale de la France ?")
    print(f"Assistant: {response1}\n")

    print("User: Quelle est sa population ?")
    response2 = conv.send("Quelle est sa population ?")
    print(f"Assistant: {response2}\n")

    print("✅ Tests terminés")
