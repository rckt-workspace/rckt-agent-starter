import httpx
from app.core.config import settings


class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.default_model = settings.agent_model
        self.fallback_model = settings.agent_fallback_model
        self.use_fallback = settings.agent_use_fallback
        self.max_tokens = settings.agent_max_tokens

    def _validate_api_key(self) -> None:
        if not self.api_key or not self.api_key.strip():
            raise ValueError("OPENROUTER_API_KEY is not configured. Please set it in your .env file.")

    async def complete(self, messages: list[dict], model: str | None = None) -> str:
        self._validate_api_key()
        model = model or self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": self.max_tokens,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

            except httpx.HTTPError as e:
                if self.use_fallback and model != self.fallback_model:
                    return await self.complete(messages, model=self.fallback_model)
                raise Exception(f"OpenRouter API error: {str(e)}")

    async def complete_with_system(
        self, system: str, user_message: str, model: str | None = None
    ) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ]
        return await self.complete(messages, model)
