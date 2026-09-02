from pathlib import Path


def load_agent_instructions() -> str:
    agent_path = Path(__file__).parent.parent.parent / "agent" / "AGENT.md"
    if not agent_path.exists():
        return "No agent instructions found."
    return agent_path.read_text(encoding="utf-8")


def load_knowledge() -> str:
    knowledge_path = Path(__file__).parent.parent.parent / "agent" / "knowledge.md"
    if not knowledge_path.exists():
        return ""
    return knowledge_path.read_text(encoding="utf-8")


def build_system_prompt() -> str:
    instructions = load_agent_instructions()
    knowledge = load_knowledge()

    prompt = f"""{instructions}

## Contexto disponible

{knowledge}"""

    return prompt.strip()
