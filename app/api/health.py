from fastapi import APIRouter
from app.schemas.chat import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok"}
