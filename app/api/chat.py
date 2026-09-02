from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, AgentInfo
from app.agent.agent import Agent
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["chat"])
_agent: Agent | None = None


def get_agent() -> Agent:
    global _agent
    if _agent is None:
        _agent = Agent()
    return _agent


@router.get("/agent", response_model=AgentInfo)
async def get_agent_info():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        agent = get_agent()
        answer = await agent.answer(request.message)
        return ChatResponse(answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error. Check logs.")
