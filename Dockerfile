#syntax=docker/dockerfile:1

# === Build stage: Install dependencies and build application ===
FROM python:3.14-slim AS builder

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/app/auth /app/app/schemas /app/app/routes

# Create models.py with all entities
RUN cat > /app/app/models.py << 'MODELS_EOF'
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fighters = relationship("Fighter", back_populates="user")
    training_sessions = relationship("TrainingSession", back_populates="user")

class WeightClass(str, enum.Enum):
    STRAWWEIGHT = "Strawweight"
    FLYWEIGHT = "Flyweight"
    BANTAMWEIGHT = "Bantamweight"
    FEATHERWEIGHT = "Featherweight"
    LIGHTWEIGHT = "Lightweight"
    MIDDLEWEIGHT = "Middleweight"
    HEAVYWEIGHT = "Heavyweight"

class Fighter(Base):
    __tablename__ = "fighters"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    nickname = Column(String, nullable=True)
    weight_class = Column(String, nullable=False)
    height = Column(Float, nullable=True)
    reach = Column(Float, nullable=True)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="fighters")
    matches_as_fighter1 = relationship("Match", foreign_keys="Match.fighter1_id", back_populates="fighter1")
    matches_as_fighter2 = relationship("Match", foreign_keys="Match.fighter2_id", back_populates="fighter2")
    training_sessions = relationship("TrainingSession", back_populates="fighter")

class EventStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=False)
    status = Column(String, default=EventStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow)
    matches = relationship("Match", back_populates="event")

class MatchStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    fighter1_id = Column(Integer, ForeignKey("fighters.id"), nullable=False)
    fighter2_id = Column(Integer, ForeignKey("fighters.id"), nullable=False)
    rounds = Column(Integer, default=12)
    duration_minutes = Column(Integer, nullable=True)
    status = Column(String, default=MatchStatus.SCHEDULED)
    winner_id = Column(Integer, ForeignKey("fighters.id"), nullable=True)
    fighter1_score = Column(Integer, nullable=True)
    fighter2_score = Column(Integer, nullable=True)
    result = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    match_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    event = relationship("Event", back_populates="matches")
    fighter1 = relationship("Fighter", foreign_keys=[fighter1_id], back_populates="matches_as_fighter1")
    fighter2 = relationship("Fighter", foreign_keys=[fighter2_id], back_populates="matches_as_fighter2")

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fighter_id = Column(Integer, ForeignKey("fighters.id"), nullable=True)
    session_type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    exercises = Column(String, nullable=True)
    intensity = Column(String, default="Medium")
    notes = Column(Text, nullable=True)
    calories_burned = Column(Integer, nullable=True)
    session_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="training_sessions")
    fighter = relationship("Fighter", back_populates="training_sessions")
MODELS_EOF

# Create schemas
RUN cat > /app/app/schemas/__init__.py << 'SCHEMAS_INIT_EOF'
from .user import UserCreate, UserResponse, UserLogin
from .fighter import FighterCreate, FighterResponse, FighterUpdate
from .match import MatchCreate, MatchResponse, MatchUpdate
from .event import EventCreate, EventResponse, EventUpdate
from .training import TrainingSessionCreate, TrainingSessionResponse
from .token import Token, TokenData
__all__ = [
    "UserCreate", "UserResponse", "UserLogin",
    "FighterCreate", "FighterResponse", "FighterUpdate",
    "MatchCreate", "MatchResponse", "MatchUpdate",
    "EventCreate", "EventResponse", "EventUpdate",
    "TrainingSessionCreate", "TrainingSessionResponse",
    "Token", "TokenData"
]
SCHEMAS_INIT_EOF

RUN cat > /app/app/schemas/user.py << 'USER_SCHEMA_EOF'
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
USER_SCHEMA_EOF

RUN cat > /app/app/schemas/fighter.py << 'FIGHTER_SCHEMA_EOF'
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

    class Config:
        from_attributes = True
FIGHTER_SCHEMA_EOF

RUN cat > /app/app/schemas/match.py << 'MATCH_SCHEMA_EOF'
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

    class Config:
        from_attributes = True
MATCH_SCHEMA_EOF

RUN cat > /app/app/schemas/event.py << 'EVENT_SCHEMA_EOF'
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: datetime

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None
    status: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    location: Optional[str]
    event_date: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
EVENT_SCHEMA_EOF

RUN cat > /app/app/schemas/training.py << 'TRAINING_SCHEMA_EOF'
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

    class Config:
        from_attributes = True
TRAINING_SCHEMA_EOF

RUN cat > /app/app/schemas/token.py << 'TOKEN_SCHEMA_EOF'
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
TOKEN_SCHEMA_EOF

# Create database connection
RUN cat > /app/app/database.py << 'DB_EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "trevor")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "supersecure")
POSTGRES_DB = os.getenv("POSTGRES_DB", "boxing")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
DB_EOF

# Create security utilities
RUN cat > /app/app/security.py << 'SECURITY_EOF'
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
SECURITY_EOF

# Create password utility (kept for compatibility)
RUN cat > /app/app/utils.py << 'UTILS_EOF'
from app.security import hash_password, verify_password
__all__ = ["hash_password", "verify_password"]
UTILS_EOF

# Update auth routes with JWT
RUN cat > /app/app/auth/routes.py << 'AUTH_ROUTES_EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas import UserCreate, UserResponse, UserLogin, Token
from app.models import User
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = decode_token(token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password),
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and get access token"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.get("/users", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Soft delete user (deactivate)"""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only delete your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    db.commit()

@router.get("/status")
def auth_status():
    """Check auth service status"""
    return {"status": "ok", "service": "auth"}
AUTH_ROUTES_EOF

# Create routes directory init
RUN touch /app/app/routes/__init__.py

# Create fighter routes
RUN cat > /app/app/routes/fighters.py << 'FIGHTERS_ROUTES_EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import FighterCreate, FighterResponse, FighterUpdate
from app.models import Fighter, User
from app.database import get_db
from app.auth.routes import get_current_user

router = APIRouter(prefix="/fighters", tags=["fighters"])

@router.post("", response_model=FighterResponse, status_code=status.HTTP_201_CREATED)
def create_fighter(fighter: FighterCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new fighter profile"""
    db_fighter = Fighter(
        user_id=current_user.id,
        name=fighter.name,
        nickname=fighter.nickname,
        weight_class=fighter.weight_class,
        height=fighter.height,
        reach=fighter.reach,
        bio=fighter.bio
    )
    db.add(db_fighter)
    db.commit()
    db.refresh(db_fighter)
    return db_fighter

@router.get("", response_model=list[FighterResponse])
def list_fighters(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all fighters"""
    fighters = db.query(Fighter).offset(skip).limit(limit).all()
    return fighters

@router.get("/{fighter_id}", response_model=FighterResponse)
def get_fighter(fighter_id: int, db: Session = Depends(get_db)):
    """Get fighter by ID"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fighter not found")
    return fighter

@router.put("/{fighter_id}", response_model=FighterResponse)
def update_fighter(fighter_id: int, fighter_update: FighterUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update fighter profile"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fighter not found")
    if fighter.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    update_data = fighter_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(fighter, key, value)
    db.commit()
    db.refresh(fighter)
    return fighter

@router.delete("/{fighter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fighter(fighter_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete fighter"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fighter not found")
    if fighter.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db.delete(fighter)
    db.commit()
FIGHTERS_ROUTES_EOF

# Create event routes
RUN cat > /app/app/routes/events.py << 'EVENTS_ROUTES_EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import EventCreate, EventResponse, EventUpdate
from app.models import Event, User
from app.database import get_db
from app.auth.routes import get_current_user

router = APIRouter(prefix="/events", tags=["events"])

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new event"""
    db_event = Event(
        name=event.name,
        description=event.description,
        location=event.location,
        event_date=event.event_date
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("", response_model=list[EventResponse])
def list_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all events"""
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_update: EventUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    update_data = event_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(event)
    db.commit()
EVENTS_ROUTES_EOF

# Create match routes
RUN cat > /app/app/routes/matches.py << 'MATCHES_ROUTES_EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import MatchCreate, MatchResponse, MatchUpdate
from app.models import Match, Fighter, User
from app.database import get_db
from app.auth.routes import get_current_user

router = APIRouter(prefix="/matches", tags=["matches"])

@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(match: MatchCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new match"""
    db_match = Match(
        fighter1_id=match.fighter1_id,
        fighter2_id=match.fighter2_id,
        event_id=match.event_id,
        rounds=match.rounds,
        match_date=match.match_date
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

@router.get("", response_model=list[MatchResponse])
def list_matches(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all matches"""
    matches = db.query(Match).offset(skip).limit(limit).all()
    return matches

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """Get match by ID"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match

@router.put("/{match_id}", response_model=MatchResponse)
def update_match(match_id: int, match_update: MatchUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update match result"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    
    update_data = match_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(match, key, value)
    
    if match.winner_id:
        fighter = db.query(Fighter).filter(Fighter.id == match.winner_id).first()
        if fighter:
            fighter.wins += 1
        loser_id = match.fighter2_id if match.winner_id == match.fighter1_id else match.fighter1_id
        loser = db.query(Fighter).filter(Fighter.id == loser_id).first()
        if loser:
            loser.losses += 1
    
    db.commit()
    db.refresh(match)
    return match

@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete match"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    db.delete(match)
    db.commit()
MATCHES_ROUTES_EOF

# Create training routes
RUN cat > /app/app/routes/training.py << 'TRAINING_ROUTES_EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import TrainingSessionCreate, TrainingSessionResponse
from app.models import TrainingSession, User
from app.database import get_db
from app.auth.routes import get_current_user

router = APIRouter(prefix="/training", tags=["training"])

@router.post("", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
def create_training_session(session: TrainingSessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Log a training session"""
    db_session = TrainingSession(
        user_id=current_user.id,
        fighter_id=session.fighter_id,
        session_type=session.session_type,
        duration_minutes=session.duration_minutes,
        exercises=session.exercises,
        intensity=session.intensity,
        notes=session.notes,
        calories_burned=session.calories_burned,
        session_date=session.session_date
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("", response_model=list[TrainingSessionResponse])
def list_training_sessions(current_user: User = Depends(get_current_user), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List training sessions for current user"""
    sessions = db.query(TrainingSession).filter(TrainingSession.user_id == current_user.id).offset(skip).limit(limit).all()
    return sessions

@router.get("/{session_id}", response_model=TrainingSessionResponse)
def get_training_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get training session by ID"""
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete training session"""
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db.delete(session)
    db.commit()
TRAINING_ROUTES_EOF

# Update auth/init
RUN touch /app/app/auth/__init__.py

# Update main.py with all routes
RUN cat > /app/app/main.py << 'MAIN_EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.auth.routes import router as auth_router
from app.routes.fighters import router as fighters_router
from app.routes.events import router as events_router
from app.routes.matches import router as matches_router
from app.routes.training import router as training_router
from app.models import Base
from app.database import engine

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create tables: {e}")

app = FastAPI(
    title=settings.APP_NAME,
    description="Boxing Management Backend API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(fighters_router)
app.include_router(events_router)
app.include_router(matches_router)
app.include_router(training_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.ENV}

@app.get("/")
def root():
    return {"message": "Boxing Management API", "version": "2.0.0"}
MAIN_EOF

# === Final stage: Create minimal runtime image ===
FROM dhi.io/python:3.14

WORKDIR /app

# Copy the entire app directory from builder
COPY --from=builder /app /app

# Copy Python site-packages from builder to the location DHI expects
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Expose port (non-privileged, as required by nonroot user)
EXPOSE 8000

# Run the application (DHI runtime images run as nonroot user by default)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
