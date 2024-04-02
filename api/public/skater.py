from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from commons.schemas import *
from backend.database import get_session
from backend.crud.skater import (
    create_skater,
    delete_skater,
    read_skater,
    read_skaters,
    update_skater,
)


router = APIRouter()


@router.post("", response_model=SkaterRead)
async def create_a_skater(skater: SkaterCreate, db: Session = Depends(get_session)):
    return create_skater(skater=skater, db=db)


@router.get("", response_model=list[SkaterReadWithClub])
async def get_skaters(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
):
    return read_skaters(offset=offset, limit=limit, db=db)


@router.get("/{skater_id}", response_model=SkaterReadWithClub)
async def get_a_skater(skater_id: int, db: Session = Depends(get_session)):
    return read_skater(skater_id=skater_id, db=db)


@router.patch("/{skater_id}", response_model=SkaterRead)
async def update_a_skater(
    skater_id: int, skater: SkaterUpdate, db: Session = Depends(get_session)
):
    return update_skater(skater_id=skater_id, skater=skater, db=db)


@router.delete("/{skater_id}")
async def delete_a_skater(skater_id: int, db: Session = Depends(get_session)):
    return delete_skater(skater_id=skater_id, db=db)
