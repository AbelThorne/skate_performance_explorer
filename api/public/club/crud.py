from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.commons.shemas import ClubCreate, ClubUpdate, Club


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
