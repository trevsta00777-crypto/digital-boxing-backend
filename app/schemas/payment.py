from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CheckoutSessionCreate(BaseModel):
    event_id: int
    quantity: int = Field(default=1, ge=1, le=20)


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
    payment_id: int


class SubscriptionStubCreate(BaseModel):
    """Optional light stub — creates Checkout in subscription mode if price id set."""
    price_id: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    event_id: Optional[int]
    payment_type: str
    amount_cents: int
    currency: str
    status: str
    stripe_checkout_session_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
