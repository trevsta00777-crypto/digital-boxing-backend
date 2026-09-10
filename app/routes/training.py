from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import TrainingSession, User
from app.schemas import TrainingSessionCreate, TrainingSessionResponse

router = APIRouter(prefix="/training", tags=["training"])


@router.post("", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
def create_training_session(
    session: TrainingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_session = TrainingSession(user_id=current_user.id, **session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("", response_model=list[TrainingSessionResponse])
def list_training_sessions(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return (
        db.query(TrainingSession)
        .filter(TrainingSession.user_id == current_user.id)
        .offset(skip)
        .limit(min(limit, 100))
        .all()
    )


@router.get("/{session_id}", response_model=TrainingSessionResponse)
def get_training_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(session)
    db.commit()
