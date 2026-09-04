from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    # Application
    app_name: str = "RCKT Agent Starter"
    app_env: str = "development"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Agent models
    agent_model: str = "openrouter/auto"
    agent_fallback_model: str = "openrouter/free"
    agent_use_fallback: bool = True

    # Agent limits
    agent_max_tokens: int = 700

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"


    # Document processing
    max_file_size_mb: int = 10
    document_max_chars: int = 50000

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
