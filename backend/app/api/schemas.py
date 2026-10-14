from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class DynamicsWebhookRequest(BaseModel):
    call_id: str = Field(min_length=1, max_length=200)
    audio_url: HttpUrl


class QueueResponse(BaseModel):
    status: str
    message: str


class CallResponse(BaseModel):
    id: UUID
    crm_activity_id: str
    date: datetime
    customer_phone: str | None
    lead_score: int
    agent_performance: str | None
    strengths: list[str]
    weaknesses: list[str]


class HealthResponse(BaseModel):
    status: str
