from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    user_id: int = Field(default=0, description="用户ID，0表示匿名")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    message: str = Field(..., min_length=1, max_length=5000, description="用户消息")
    message_type: str = Field(default="text", description="消息类型")


class ChatResponse(BaseModel):
    session_id: str
    message_id: int
    intent: str = ""
    sentiment: str = "neutral"
    confidence: float = 0.0
    knowledge_sources: list[str] = []


class FeedbackRequest(BaseModel):
    message_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""
