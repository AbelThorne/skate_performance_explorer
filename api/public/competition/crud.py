from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.public.competition.models import (
    Competition,
    CompetitionCreate,
    CompetitionUpdate,
)


def create_competition(
    competition: CompetitionCreate, db: Session = Depends(get_session)
):
    competition_to_db = Competition.model_validate(competition)
    db.add(competition_to_db)
    db.commit()
    db.refresh(competition_to_db)
    return competition_to_db


def read_competitions(
    offset: int = 0, limit: int = 20, db: Session = Depends(get_session)
):
    competitions = db.exec(select(Competition).offset(offset).limit(limit)).all()
    return competitions


def read_competition(competition_id: int, db: Session = Depends(get_session)):
    competition = db.get(Competition, competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competition not found with id: {competition_id}",
        )
    return competition


def update_competition(
    competition_id: int,
    competition: CompetitionUpdate,
    db: Session = Depends(get_session),
):
    competition_to_update = db.get(Competition, competition_id)
    if not competition_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competition not found with id: {competition_id}",
        )

    competition_data = competition.model_dump(exclude_unset=True)
    competition_to_update.sqlmodel_update(competition_data)
    db.add(competition_to_update)
    db.commit()
    db.refresh(competition_to_update)
    return competition_to_update


def delete_competition(competition_id: int, db: Session = Depends(get_session)):
    competition = db.get(Competition, competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competition not found with id: {competition_id}",
        )

    db.delete(competition)
    db.commit()
    return {"ok": True}
