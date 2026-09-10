from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MatchCreate(BaseModel):
    fighter1_id: int
    fighter2_id: int
    event_id: Optional[int] = None
    rounds: int = 12
    match_date: datetime


class MatchUpdate(BaseModel):
    status: Optional[str] = None
    winner_id: Optional[int] = None
    fighter1_score: Optional[int] = None
    fighter2_score: Optional[int] = None
    result: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class MatchResponse(BaseModel):
    id: int
    event_id: Optional[int]
    fighter1_id: int
    fighter2_id: int
    rounds: int
    duration_minutes: Optional[int]
    status: str
    winner_id: Optional[int]
    fighter1_score: Optional[int]
    fighter2_score: Optional[int]
    result: Optional[str]
    notes: Optional[str]
    match_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
