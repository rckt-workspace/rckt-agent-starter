from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str


class AgentInfo(BaseModel):
    name: str
    version: str = "1.0.0"


class HealthResponse(BaseModel):
    status: str
