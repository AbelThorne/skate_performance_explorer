from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.public.skater.models import Skater, SkaterCreate, SkaterUpdate


def create_skater(skater: SkaterCreate, db: Session = Depends(get_session)):
    skater_to_db = Skater.model_validate(skater)
    db.add(skater_to_db)
    db.commit()
    db.refresh(skater_to_db)
    return skater_to_db


def read_skaters(offset: int = 0, limit: int = 20, db: Session = Depends(get_session)):
    skaters = db.exec(select(Skater).offset(offset).limit(limit)).all()
    return skaters


def read_skater(skater_id: int, db: Session = Depends(get_session)):
    skater = db.get(Skater, skater_id)
    if not skater:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skater not found with id: {skater_id}",
        )
    return skater


def update_skater(
    skater_id: int, skater: SkaterUpdate, db: Session = Depends(get_session)
):
    skater_to_update = db.get(Skater, skater_id)
    if not skater_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skater not found with id: {skater_id}",
        )

    team_data = skater.model_dump(exclude_unset=True)
    for key, value in team_data.items():
        setattr(skater_to_update, key, value)

    db.add(skater_to_update)
    db.commit()
    db.refresh(skater_to_update)
    return skater_to_update


def delete_skater(skater_id: int, db: Session = Depends(get_session)):
    skater = db.get(Skater, skater_id)
    if not skater:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skater not found with id: {skater_id}",
        )

    db.delete(skater)
    db.commit()
    return {"ok": True}
