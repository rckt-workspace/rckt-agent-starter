#!/usr/bin/env python
"""Debug script to verify OpenRouter API key configuration flow."""
import asyncio
from app.core.config import settings
from app.llm.openrouter import OpenRouterClient
from app.agent.agent import Agent

async def main():
    print("=" * 70)
    print("VERIFICACIÓN DE CONFIGURACIÓN - OPENROUTER API KEY")
    print("=" * 70)

    # Step 1: Verificar settings
    print("\n1. SETTINGS (app.core.config.settings)")
    print("-" * 70)
    settings_key = settings.openrouter_api_key
    settings_configured = bool(settings_key and settings_key.strip())
    settings_length = len(settings_key) if settings_key else 0

    print(f"   settings.openrouter_api_key configured: {settings_configured}")
    print(f"   settings.openrouter_api_key length: {settings_length}")
    if settings_configured:
        print(f"   First 20 chars (obfuscated): {settings_key[:20]}...")

    # Step 2: Crear cliente y verificar
    print("\n2. OPENROUTER CLIENT INITIALIZATION")
    print("-" * 70)
    try:
        client = OpenRouterClient()
        client_key = client.api_key
        client_configured = bool(client_key and client_key.strip())
        client_length = len(client_key) if client_key else 0

        print(f"   client.api_key configured: {client_configured}")
        print(f"   client.api_key length: {client_length}")
        if client_configured:
            print(f"   First 20 chars (obfuscated): {client_key[:20]}...")

        # Step 3: Verificar que los valores coinciden
        print("\n3. COMPARACIÓN SETTINGS vs CLIENT")
        print("-" * 70)
        if settings_key == client_key:
            print("   ✓ API keys coinciden perfectamente")
        else:
            print("   ✗ PROBLEMA: API keys NO coinciden")
            print(f"     settings value == client value: {settings_key == client_key}")

        # Step 4: Verificar flujo de autorización
        print("\n4. FLUJO DE AUTORIZACIÓN (conceptual)")
        print("-" * 70)
        print("   settings.openrouter_api_key")
        print("         ↓")
        print("   OpenRouterClient.__init__() → self.api_key = settings.openrouter_api_key")
        print("         ↓")
        print("   OpenRouterClient.complete() → headers['Authorization'] = f'Bearer {self.api_key}'")
        print("         ↓")
        print("   POST https://openrouter.ai/api/v1/chat/completions")

        # Step 5: Verificar método de validación
        print("\n5. VALIDACIÓN DE API KEY")
        print("-" * 70)
        try:
            client._validate_api_key()
            print("   ✓ _validate_api_key() pasó correctamente")
        except ValueError as e:
            print(f"   ✗ _validate_api_key() falló: {e}")

        # Step 6: Información del cliente
        print("\n6. CONFIGURACIÓN DEL CLIENTE OPENROUTER")
        print("-" * 70)
        print(f"   base_url: {client.base_url}")
        print(f"   default_model: {client.default_model}")
        print(f"   fallback_model: {client.fallback_model}")
        print(f"   use_fallback: {client.use_fallback}")
        print(f"   max_tokens: {client.max_tokens}")

    except Exception as e:
        print(f"   ✗ Error al crear OpenRouterClient: {e}")

    # Step 7: Verificar Agent
    print("\n7. AGENT INITIALIZATION")
    print("-" * 70)
    try:
        agent = Agent()
        print("   ✓ Agent creado exitosamente")
        print(f"   Agent client type: {type(agent.client).__name__}")
        print(f"   Agent client api_key configured: {bool(agent.client.api_key and agent.client.api_key.strip())}")
    except Exception as e:
        print(f"   ✗ Error al crear Agent: {e}")

    print("\n" + "=" * 70)
    print("CONCLUSIÓN")
    print("=" * 70)
    if settings_configured and client_configured and settings_key == client_key:
        print("✓ TODO ESTÁ CORRECTAMENTE CONFIGURADO")
        print("  La API key fluye correctamente desde settings → client → headers")
    else:
        print("✗ PROBLEMA DETECTADO - Revisar arriba")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
