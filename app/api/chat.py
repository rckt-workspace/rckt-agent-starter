import logging
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.schemas.chat import ChatRequest, ChatResponse, AgentInfo
from app.agent.agent import Agent
from app.core.config import settings
from app.documents.validators import validate_document_file
from app.documents.parser import parse_document

logger = logging.getLogger(__name__)

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
        err_msg = str(e)
        if "OpenRouter" in err_msg or "AI service" in err_msg:
            raise HTTPException(status_code=503, detail="AI service unavailable. Please try again later.")
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Check logs.")


@router.post("/chat/document", response_model=ChatResponse)
async def chat_document(
    message: str = Form(..., min_length=1, max_length=2000),
    file: UploadFile = File(...),
):
    if not message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty or only whitespace.")

    try:
        content_bytes = await validate_document_file(file)
        document_text = parse_document(file.filename or "", content_bytes)

        agent = get_agent()
        answer = await agent.answer(user_message=message.strip(), additional_context=document_text)
        return ChatResponse(answer=answer)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        err_msg = str(e)
        if "OpenRouter" in err_msg or "AI service" in err_msg:
            raise HTTPException(status_code=503, detail="AI service unavailable. Please try again later.")
        logger.error(f"Error in chat_document endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Check logs.")
