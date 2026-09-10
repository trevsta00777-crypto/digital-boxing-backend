from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Fighter, Match, MatchStatus, User
from app.schemas import MatchCreate, MatchResponse, MatchUpdate

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    match: MatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if match.fighter1_id == match.fighter2_id:
        raise HTTPException(status_code=400, detail="Fighters must be different")
    for fid in (match.fighter1_id, match.fighter2_id):
        if not db.query(Fighter).filter(Fighter.id == fid).first():
            raise HTTPException(status_code=404, detail=f"Fighter {fid} not found")
    db_match = Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@router.get("", response_model=list[MatchResponse])
def list_matches(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Match).offset(skip).limit(min(limit, 100)).all()


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.put("/{match_id}", response_model=MatchResponse)
def update_match(
    match_id: int,
    match_update: MatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    data = match_update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(match, key, value)
    if data.get("winner_id") and data.get("status") == MatchStatus.COMPLETED.value:
        winner = db.query(Fighter).filter(Fighter.id == match.winner_id).first()
        if winner:
            winner.wins += 1
        loser_id = (
            match.fighter2_id
            if match.winner_id == match.fighter1_id
            else match.fighter1_id
        )
        loser = db.query(Fighter).filter(Fighter.id == loser_id).first()
        if loser:
            loser.losses += 1
    db.commit()
    db.refresh(match)
    return match


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    db.commit()
