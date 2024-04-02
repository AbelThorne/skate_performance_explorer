from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from backend.database import get_session
from commons.schemas import *


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

    skater_data = skater.model_dump(exclude_unset=True)
    skater_to_update.sqlmodel_update(skater_data)
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


def find_or_create_skater(
    query: SelectOfScalar[Skater],
    skater: SkaterCreate,
    db: Session = Depends(get_session),
):
    query_result = db.exec(query).first()
    if query_result:
        return query_result
    else:
        return create_skater(skater, db)


# def skater_get_or_create(skater: Skater, db: Session = Depends(get_session)):
#     """Get a skater from the database or create it if it doesn't exist."""
#     skater_db = db.exec(
#         select(Skater)
#         .where(Skater.full_name == skater.full_name)
#         .where(Skater.genre == skater.genre)
#     ).first()

#     if skater_db is None:
#         skater_db = Skater.model_validate(skater)
#         db.add(skater_db)
#         db.commit()
#         db.refresh(skater_db)
#     return skater_db
