from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TrainingSessionCreate(BaseModel):
    session_type: str
    duration_minutes: int
    exercises: Optional[str] = None
    intensity: str = "Medium"
    notes: Optional[str] = None
    calories_burned: Optional[int] = None
    fighter_id: Optional[int] = None
    session_date: datetime


class TrainingSessionResponse(BaseModel):
    id: int
    user_id: int
    fighter_id: Optional[int]
    session_type: str
    duration_minutes: int
    exercises: Optional[str]
    intensity: str
    notes: Optional[str]
    calories_burned: Optional[int]
    session_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
