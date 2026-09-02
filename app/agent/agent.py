from app.llm.openrouter import OpenRouterClient
from app.agent.prompt_loader import build_system_prompt


class Agent:
    def __init__(self):
        self.client = OpenRouterClient()
        self.system_prompt = build_system_prompt()

    async def answer(self, user_message: str) -> str:
        response = await self.client.complete_with_system(
            system=self.system_prompt,
            user_message=user_message,
        )
        return response
