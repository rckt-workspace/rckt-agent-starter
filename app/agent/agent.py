from app.llm.openrouter import OpenRouterClient
from app.agent.prompt_loader import build_system_prompt


class Agent:
    def __init__(self):
        self.client = OpenRouterClient()
        self.system_prompt = build_system_prompt()

    async def answer(self, user_message: str, additional_context: str | None = None) -> str:
        system = self.system_prompt
        if additional_context and additional_context.strip():
            system = f"{self.system_prompt}\n\n## Contexto del documento adjunto\n\n{additional_context.strip()}"

        response = await self.client.complete_with_system(
            system=system,
            user_message=user_message,
        )
        return response
