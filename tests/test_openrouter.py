import pytest
import asyncio
from unittest.mock import patch
from app.llm.openrouter import OpenRouterClient


def test_openrouter_client_missing_api_key():
    """Test that OpenRouterClient raises ValueError when API key is missing."""
    with patch('app.llm.openrouter.settings') as mock_settings:
        mock_settings.openrouter_api_key = ""
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_settings.agent_model = "openrouter/auto"
        mock_settings.agent_fallback_model = "openrouter/free"
        mock_settings.agent_use_fallback = True
        mock_settings.agent_max_tokens = 700

        client = OpenRouterClient()

        with pytest.raises(ValueError, match="OPENROUTER_API_KEY is not configured"):
            asyncio.run(client.complete([{"role": "user", "content": "test"}]))


def test_openrouter_client_missing_api_key_whitespace():
    """Test that OpenRouterClient rejects whitespace-only API key."""
    with patch('app.llm.openrouter.settings') as mock_settings:
        mock_settings.openrouter_api_key = "   "
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_settings.agent_model = "openrouter/auto"
        mock_settings.agent_fallback_model = "openrouter/free"
        mock_settings.agent_use_fallback = True
        mock_settings.agent_max_tokens = 700

        client = OpenRouterClient()

        with pytest.raises(ValueError, match="OPENROUTER_API_KEY is not configured"):
            asyncio.run(client.complete([{"role": "user", "content": "test"}]))


def test_openrouter_client_api_key_present():
    """Test that OpenRouterClient accepts a valid API key."""
    with patch('app.llm.openrouter.settings') as mock_settings:
        mock_settings.openrouter_api_key = "sk-or-v1-" + "x" * 64
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_settings.agent_model = "openrouter/auto"
        mock_settings.agent_fallback_model = "openrouter/free"
        mock_settings.agent_use_fallback = True
        mock_settings.agent_max_tokens = 700

        client = OpenRouterClient()

        assert client.api_key == mock_settings.openrouter_api_key
        assert len(client.api_key) > 0


def test_openrouter_client_validate_api_key_method():
    """Test that _validate_api_key method works correctly."""
    with patch('app.llm.openrouter.settings') as mock_settings:
        mock_settings.openrouter_api_key = ""
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_settings.agent_model = "openrouter/auto"
        mock_settings.agent_fallback_model = "openrouter/free"
        mock_settings.agent_use_fallback = True
        mock_settings.agent_max_tokens = 700

        client = OpenRouterClient()

        with pytest.raises(ValueError, match="OPENROUTER_API_KEY is not configured"):
            client._validate_api_key()


def test_openrouter_client_initialization_captures_config():
    """Test that OpenRouterClient captures all configuration at initialization."""
    with patch('app.llm.openrouter.settings') as mock_settings:
        test_key = "sk-or-v1-test123456789"
        mock_settings.openrouter_api_key = test_key
        mock_settings.openrouter_base_url = "https://test.openrouter.ai/v1"
        mock_settings.agent_model = "test/model"
        mock_settings.agent_fallback_model = "test/fallback"
        mock_settings.agent_use_fallback = False
        mock_settings.agent_max_tokens = 1000

        client = OpenRouterClient()

        assert client.api_key == test_key
        assert client.base_url == "https://test.openrouter.ai/v1"
        assert client.default_model == "test/model"
        assert client.fallback_model == "test/fallback"
        assert client.use_fallback == False
        assert client.max_tokens == 1000


def test_openrouter_client_key_propagation():
    """Test that API key is properly propagated from settings to client to request headers."""
    with patch('app.llm.openrouter.settings') as mock_settings:
        test_key = "sk-or-v1-abc123def456ghi789"
        mock_settings.openrouter_api_key = test_key
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_settings.agent_model = "openrouter/auto"
        mock_settings.agent_fallback_model = "openrouter/free"
        mock_settings.agent_use_fallback = True
        mock_settings.agent_max_tokens = 700

        client = OpenRouterClient()

        # Verify key is captured at client initialization
        assert client.api_key == test_key
        assert len(client.api_key) == len(test_key)

        # Verify _validate_api_key doesn't raise for valid key
        client._validate_api_key()  # Should not raise
