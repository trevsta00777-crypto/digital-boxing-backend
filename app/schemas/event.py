from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: datetime
    ticket_price_cents: int = Field(default=0, ge=0)
    currency: str = "usd"


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None
    status: Optional[str] = None
    ticket_price_cents: Optional[int] = Field(default=None, ge=0)
    currency: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    location: Optional[str]
    event_date: datetime
    status: str
    ticket_price_cents: int
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}
