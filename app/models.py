import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class WeightClass(str, enum.Enum):
    STRAWWEIGHT = "Strawweight"
    FLYWEIGHT = "Flyweight"
    BANTAMWEIGHT = "Bantamweight"
    FEATHERWEIGHT = "Featherweight"
    LIGHTWEIGHT = "Lightweight"
    MIDDLEWEIGHT = "Middleweight"
    HEAVYWEIGHT = "Heavyweight"


class EventStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class MatchStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentType(str, enum.Enum):
    EVENT_TICKET = "event_ticket"
    SUBSCRIPTION = "subscription"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fighters = relationship("Fighter", back_populates="user")
    training_sessions = relationship("TrainingSession", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Fighter(Base):
    __tablename__ = "fighters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=True)
    weight_class = Column(String(50), nullable=False)
    height = Column(Float, nullable=True)
    reach = Column(Float, nullable=True)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="fighters")
    matches_as_fighter1 = relationship(
        "Match", foreign_keys="Match.fighter1_id", back_populates="fighter1"
    )
    matches_as_fighter2 = relationship(
        "Match", foreign_keys="Match.fighter2_id", back_populates="fighter2"
    )
    training_sessions = relationship("TrainingSession", back_populates="fighter")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    event_date = Column(DateTime, nullable=False)
    status = Column(String(50), default=EventStatus.SCHEDULED.value)
    ticket_price_cents = Column(Integer, default=0)
    currency = Column(String(10), default="usd")
    created_at = Column(DateTime, default=datetime.utcnow)

    matches = relationship("Match", back_populates="event")
    payments = relationship("Payment", back_populates="event")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    fighter1_id = Column(Integer, ForeignKey("fighters.id"), nullable=False)
    fighter2_id = Column(Integer, ForeignKey("fighters.id"), nullable=False)
    rounds = Column(Integer, default=12)
    duration_minutes = Column(Integer, nullable=True)
    status = Column(String(50), default=MatchStatus.SCHEDULED.value)
    winner_id = Column(Integer, ForeignKey("fighters.id"), nullable=True)
    fighter1_score = Column(Integer, nullable=True)
    fighter2_score = Column(Integer, nullable=True)
    result = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    match_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="matches")
    fighter1 = relationship(
        "Fighter", foreign_keys=[fighter1_id], back_populates="matches_as_fighter1"
    )
    fighter2 = relationship(
        "Fighter", foreign_keys=[fighter2_id], back_populates="matches_as_fighter2"
    )


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fighter_id = Column(Integer, ForeignKey("fighters.id"), nullable=True)
    session_type = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    exercises = Column(String(500), nullable=True)
    intensity = Column(String(50), default="Medium")
    notes = Column(Text, nullable=True)
    calories_burned = Column(Integer, nullable=True)
    session_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="training_sessions")
    fighter = relationship("Fighter", back_populates="training_sessions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    payment_type = Column(String(50), default=PaymentType.EVENT_TICKET.value)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(10), default="usd")
    status = Column(String(50), default=PaymentStatus.PENDING.value)
    stripe_checkout_session_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_payment_intent_id = Column(String(255), nullable=True, index=True)
    stripe_customer_id = Column(String(255), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="payments")
    event = relationship("Event", back_populates="payments")
