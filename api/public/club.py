from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from backend.database import get_session
from backend.crud.club import (
    create_club,
    read_club,
    read_clubs,
    update_club,
    delete_club,
)

from commons.shemas import *

router = APIRouter()


@router.post("", response_model=ClubRead)
def create_a_club(club: ClubCreate, db: Session = Depends(get_session)):
    return create_club(club=club, db=db)


@router.get("", response_model=list[ClubRead])
def get_clubs(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
):
    return read_clubs(offset=offset, limit=limit, db=db)


@router.get("/{club_id}", response_model=ClubRead)
def get_a_club(club_id: int, db: Session = Depends(get_session)):
    return read_club(club_id=club_id, db=db)


@router.patch("/{club_id}", response_model=ClubRead)
def update_a_club(club_id: int, club: ClubUpdate, db: Session = Depends(get_session)):
    return update_club(club_id=club_id, club=club, db=db)


@router.delete("/{club_id}")
def delete_a_club(club_id: int, db: Session = Depends(get_session)):
    return delete_club(club_id=club_id, db=db)
