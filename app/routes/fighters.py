from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Fighter, User
from app.schemas import FighterCreate, FighterResponse, FighterUpdate

router = APIRouter(prefix="/fighters", tags=["fighters"])


@router.post("", response_model=FighterResponse, status_code=status.HTTP_201_CREATED)
def create_fighter(
    fighter: FighterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_fighter = Fighter(user_id=current_user.id, **fighter.model_dump())
    db.add(db_fighter)
    db.commit()
    db.refresh(db_fighter)
    return db_fighter


@router.get("", response_model=list[FighterResponse])
def list_fighters(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Fighter).offset(skip).limit(min(limit, 100)).all()


@router.get("/{fighter_id}", response_model=FighterResponse)
def get_fighter(fighter_id: int, db: Session = Depends(get_db)):
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    return fighter


@router.put("/{fighter_id}", response_model=FighterResponse)
def update_fighter(
    fighter_id: int,
    fighter_update: FighterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    if fighter.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for key, value in fighter_update.model_dump(exclude_unset=True).items():
        setattr(fighter, key, value)
    db.commit()
    db.refresh(fighter)
    return fighter


@router.delete("/{fighter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fighter(
    fighter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    if fighter.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(fighter)
    db.commit()
