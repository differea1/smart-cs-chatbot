from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class DashboardResponse(BaseModel):
    total_conversations: int = 0
    today_conversations: int = 0
    avg_satisfaction: float = 0.0
    escalation_rate: float = 0.0
