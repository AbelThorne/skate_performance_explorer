from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from backend.database import get_session
from commons.schemas import *


def create_club(club: ClubCreate, db: Session = Depends(get_session)):
    club_to_db = Club.model_validate(club)
    db.add(club_to_db)
    db.commit()
    db.refresh(club_to_db)
    return club_to_db


def read_clubs(offset: int = 0, limit: int = 20, db: Session = Depends(get_session)):
    clubs = db.exec(select(Club).offset(offset).limit(limit)).all()
    return clubs


def read_club(club_id: int, db: Session = Depends(get_session)):
    club = db.get(Club, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Club not found with id: {club_id}",
        )
    return club


def update_club(
    club_id: int,
    club: ClubUpdate,
    db: Session = Depends(get_session),
):
    club_to_update = db.get(Club, club_id)
    if not club_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Club not found with id: {club_id}",
        )

    club_data = club.model_dump(exclude_unset=True)
    club_to_update.sqlmodel_update(club_data)
    db.add(club_to_update)
    db.commit()
    db.refresh(club_to_update)
    return club_to_update


def delete_club(club_id: int, db: Session = Depends(get_session)):
    club = db.get(Club, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Club not found with id: {club_id}",
        )

    db.delete(club)
    db.commit()
    return {"ok": True}


def club_get_or_create(club: Club, db: Session = Depends(get_session)):
    """Get a club from the database or create it if it doesn't exist."""
    if club is None or club.abbrev is None:
        return None

    club_db = db.exec(select(Club).where(Club.abbrev == club.abbrev)).first()
    if club_db is None:
        club_db = Club.model_validate(club)
        db.add(club_db)
        db.commit()
        db.refresh(club_db)
    return club_db
