#!/usr/bin/env python
"""
Verify API key propagation from settings -> OpenRouterClient -> request headers.
Does NOT print actual key values.
"""
import asyncio
from app.core.config import settings
from app.llm.openrouter import OpenRouterClient
from app.agent.agent import Agent

def verify_settings_key():
    """Check if settings has API key configured."""
    has_key = bool(settings.openrouter_api_key and settings.openrouter_api_key.strip())
    key_length = len(settings.openrouter_api_key) if settings.openrouter_api_key else 0
    return has_key, key_length

def verify_client_key():
    """Check if OpenRouterClient captures the key."""
    try:
        client = OpenRouterClient()
        has_key = bool(client.api_key and client.api_key.strip())
        key_length = len(client.api_key) if client.api_key else 0
        return has_key, key_length, client
    except Exception as e:
        return False, 0, None

def verify_agent_client_key():
    """Check if Agent -> OpenRouterClient propagates the key."""
    try:
        agent = Agent()
        has_key = bool(agent.client.api_key and agent.client.api_key.strip())
        key_length = len(agent.client.api_key) if agent.client.api_key else 0
        return has_key, key_length
    except Exception as e:
        return False, 0

def main():
    print("=" * 80)
    print("API KEY PROPAGATION VERIFICATION")
    print("=" * 80)

    # Step 1: Settings
    settings_has_key, settings_key_len = verify_settings_key()
    print(f"\n1. Settings (app.core.config)")
    print(f"   - openrouter_api_key configured: {settings_has_key}")
    print(f"   - Key length: {settings_key_len}")

    # Step 2: OpenRouterClient
    client_has_key, client_key_len, client = verify_client_key()
    print(f"\n2. OpenRouterClient (app.llm.openrouter)")
    print(f"   - api_key configured: {client_has_key}")
    print(f"   - Key length: {client_key_len}")

    if not client:
        print("   ⚠️ ISSUE: Failed to create OpenRouterClient")
        return

    # Step 3: Agent
    agent_has_key, agent_key_len = verify_agent_client_key()
    print(f"\n3. Agent -> OpenRouterClient (app.agent.agent)")
    print(f"   - client.api_key configured: {agent_has_key}")
    print(f"   - Key length: {agent_key_len}")

    # Step 4: Request headers simulation
    print(f"\n4. Request Headers (would include Authorization)")
    if client:
        print(f"   - Authorization header would be: 'Bearer {len(client.api_key)}' chars")
        if client_has_key:
            print(f"   ✓ Header can be constructed")
        else:
            print(f"   ✗ Header CANNOT be constructed (empty key)")

    # Step 5: Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    if settings_key_len == 0:
        print("❌ CRITICAL: settings.openrouter_api_key is empty or missing")
        print("   Action: Check .env file has OPENROUTER_API_KEY set")
    elif client_key_len == 0:
        print("❌ CRITICAL: OpenRouterClient.api_key is empty")
        print("   The key is lost between settings and client!")
        print("   Expected flow: settings.openrouter_api_key -> client.api_key")
    elif settings_key_len != client_key_len:
        print(f"❌ CRITICAL: Key length mismatch!")
        print(f"   settings: {settings_key_len} chars")
        print(f"   client: {client_key_len} chars")
    else:
        print("✓ Settings has key configured")
        print("✓ OpenRouterClient captured the key")
        if agent_has_key:
            print("✓ Agent -> OpenRouterClient chain is intact")
        else:
            print("❌ Agent cannot access the key")

    print("=" * 80)

if __name__ == "__main__":
    main()
