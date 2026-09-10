from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FighterCreate(BaseModel):
    name: str
    nickname: Optional[str] = None
    weight_class: str
    height: Optional[float] = None
    reach: Optional[float] = None
    bio: Optional[str] = None


class FighterUpdate(BaseModel):
    name: Optional[str] = None
    nickname: Optional[str] = None
    weight_class: Optional[str] = None
    height: Optional[float] = None
    reach: Optional[float] = None
    bio: Optional[str] = None


class FighterResponse(BaseModel):
    id: int
    user_id: int
    name: str
    nickname: Optional[str]
    weight_class: str
    height: Optional[float]
    reach: Optional[float]
    wins: int
    losses: int
    draws: int
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
