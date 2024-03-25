from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from backend.database import get_session
from commons.schemas import InscriptionCreate, InscriptionUpdate, Inscription


def create_inscription(
    inscription: InscriptionCreate, db: Session = Depends(get_session)
):
    inscription_to_db = Inscription.model_validate(inscription)
    db.add(inscription_to_db)
    db.commit()
    db.refresh(inscription_to_db)
    return inscription_to_db


def read_inscriptions(
    offset: int = 0, limit: int = 20, db: Session = Depends(get_session)
):
    inscriptions = db.exec(select(Inscription).offset(offset).limit(limit)).all()
    return inscriptions


def read_inscription(inscription_id: int, db: Session = Depends(get_session)):
    inscription = db.get(Inscription, inscription_id)
    if not inscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscription not found with id: {inscription_id}",
        )
    return inscription


def update_inscription(
    inscription_id: int,
    inscription: InscriptionUpdate,
    db: Session = Depends(get_session),
):
    inscription_to_update = db.get(Inscription, inscription_id)
    if not inscription_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscription not found with id: {inscription_id}",
        )

    inscription_data = inscription.model_dump(exclude_unset=True)
    inscription_to_update.sqlmodel_update(inscription_data)
    db.add(inscription_to_update)
    db.commit()
    db.refresh(inscription_to_update)
    return inscription_to_update


def delete_inscription(inscription_id: int, db: Session = Depends(get_session)):
    inscription = db.get(Inscription, inscription_id)
    if not inscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscription not found with id: {inscription_id}",
        )

    db.delete(inscription)
    db.commit()
    return {"ok": True}
