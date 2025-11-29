"""
Script de test pour l'API Rowboat SDK Connector

Ce script teste tous les endpoints de l'API.
"""

import requests
import json
import sys


# Configuration
BASE_URL = "http://localhost:8000"


def print_section(title):
    """Affiche un séparateur de section."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_health():
    """Test l'endpoint /health."""
    print_section("TEST: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()

        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Version: {data['version']}")
        print(f"✅ Rowboat configuré: {data['rowboat_configured']}")

        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_config():
    """Test l'endpoint /config."""
    print_section("TEST: Configuration")

    try:
        response = requests.get(f"{BASE_URL}/config")
        response.raise_for_status()

        data = response.json()
        print(json.dumps(data, indent=2))

        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_chat_simple():
    """Test l'endpoint /chat avec un message simple."""
    print_section("TEST: Chat Simple")

    try:
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Quelle est la capitale de la France ?"
                }
            ]
        }

        print("Envoi de la requête...")
        print(json.dumps(payload, indent=2))

        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()

        data = response.json()
        print("\nRéponse:")
        print(f"✅ Message: {data['response']}")
        print(f"✅ Conversation ID: {data['conversation_id']}")

        return data['conversation_id']
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if hasattr(e, 'response'):
            print(f"Détails: {e.response.text}")
        return None


def test_chat_continuation(conversation_id):
    """Test la continuation d'une conversation."""
    print_section("TEST: Continuation de Conversation")

    if not conversation_id:
        print("⚠️  Pas de conversation_id, test ignoré")
        return False

    try:
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Quelle est sa population ?"
                }
            ],
            "conversation_id": conversation_id
        }

        print(f"Continuation de la conversation {conversation_id}...")
        print(json.dumps(payload, indent=2))

        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()

        data = response.json()
        print("\nRéponse:")
        print(f"✅ Message: {data['response']}")
        print(f"✅ Conversation ID: {data['conversation_id']}")

        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if hasattr(e, 'response'):
            print(f"Détails: {e.response.text}")
        return False


def test_owui():
    """Test l'endpoint OpenWebUI."""
    print_section("TEST: OpenWebUI Endpoint")

    try:
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Bonjour, qui es-tu ?"
                }
            ],
            "debug": True
        }

        print("Envoi de la requête avec debug activé...")
        print(json.dumps(payload, indent=2))

        response = requests.post(f"{BASE_URL}/owui", json=payload)
        response.raise_for_status()

        data = response.json()
        print("\nRéponse:")
        print(f"✅ Message: {data['response']}")
        print(f"✅ Conversation ID: {data['conversation_id']}")

        if 'metadata' in data:
            print("\nMetadata:")
            print(json.dumps(data['metadata'], indent=2))

        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if hasattr(e, 'response'):
            print(f"Détails: {e.response.text}")
        return False


def test_mock_tools():
    """Test l'utilisation de mock tools."""
    print_section("TEST: Mock Tools")

    try:
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Quel temps fait-il à Paris ?"
                }
            ],
            "mock_tools": {
                "weather_lookup": "Il fait beau et 25°C à Paris."
            }
        }

        print("Envoi de la requête avec mock tools...")
        print(json.dumps(payload, indent=2))

        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()

        data = response.json()
        print("\nRéponse:")
        print(f"✅ Message: {data['response']}")

        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if hasattr(e, 'response'):
            print(f"Détails: {e.response.text}")
        return False


def main():
    """Fonction principale."""
    print("\n" + "🧪 " + "="*58)
    print("   Tests API Rowboat SDK Connector")
    print("="*60 + "\n")

    print(f"URL de base: {BASE_URL}\n")

    results = []

    # Test 1: Health check
    results.append(("Health Check", test_health()))

    # Test 2: Configuration
    results.append(("Configuration", test_config()))

    # Test 3: Chat simple
    conversation_id = test_chat_simple()
    results.append(("Chat Simple", conversation_id is not None))

    # Test 4: Continuation de conversation
    results.append(("Continuation", test_chat_continuation(conversation_id)))

    # Test 5: OpenWebUI
    results.append(("OpenWebUI", test_owui()))

    # Test 6: Mock Tools
    results.append(("Mock Tools", test_mock_tools()))

    # Résumé
    print_section("RÉSUMÉ DES TESTS")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{passed}/{total} tests réussis")

    if passed == total:
        print("\n🎉 Tous les tests sont passés !")
        sys.exit(0)
    else:
        print("\n⚠️  Certains tests ont échoué")
        sys.exit(1)


if __name__ == "__main__":
    main()
