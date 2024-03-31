from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from commons.schemas import *
from backend.database import get_session
from backend.crud.competition import (
    create_competition,
    read_competition,
    read_competitions,
    update_competition,
    delete_competition,
)


router = APIRouter()


@router.post("", response_model=CompetitionRead)
async def create_a_competition(
    competition: CompetitionCreate, db: Session = Depends(get_session)
):
    return create_competition(competition=competition, db=db)


@router.get("", response_model=list[CompetitionRead])
async def get_competitions(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
):
    return read_competitions(offset=offset, limit=limit, db=db)


@router.get("/{competition_id}", response_model=CompetitionRead)
async def get_a_competition(competition_id: int, db: Session = Depends(get_session)):
    return read_competition(competition_id=competition_id, db=db)


@router.patch("/{competition_id}", response_model=CompetitionRead)
async def update_a_competition(
    competition_id: int,
    competition: CompetitionUpdate,
    db: Session = Depends(get_session),
):
    return update_competition(
        competition_id=competition_id, competition=competition, db=db
    )


@router.delete("/{competition_id}")
async def delete_a_competition(competition_id: int, db: Session = Depends(get_session)):
    return delete_competition(competition_id=competition_id, db=db)
