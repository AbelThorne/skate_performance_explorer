from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.database import get_session
from api.public.competition.crud import (
    create_competition,
    read_competition,
    read_competitions,
    update_competition,
    delete_competition,
)
from api.public.competition.models import (
    CompetitionCreate,
    CompetitionRead,
    CompetitionUpdate,
)

router = APIRouter()


@router.post("", response_model=CompetitionRead)
def create_a_competition(
    competition: CompetitionCreate, db: Session = Depends(get_session)
):
    return create_competition(competition=competition, db=db)


@router.get("", response_model=list[CompetitionRead])
def get_competitions(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
):
    return read_competitions(offset=offset, limit=limit, db=db)


@router.get("/{competition_id}", response_model=CompetitionRead)
def get_a_competition(competition_id: int, db: Session = Depends(get_session)):
    return read_competition(competition_id=competition_id, db=db)


# @router.patch("/{competition_id}", response_model=CompetitionRead)
# def update_a_competition(
#     competition_id: int,
#     competition: CompetitionUpdate,
#     db: Session = Depends(get_session),
# ):
#     return update_competition(
#         competition_id=competition_id, competition=competition, db=db
#     )


@router.delete("/{competition_id}")
def delete_a_competition(competition_id: int, db: Session = Depends(get_session)):
    return delete_competition(competition_id=competition_id, db=db)
