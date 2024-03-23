from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.database import get_session
from api.public.performance.crud import (
    create_performance,
    read_performance,
    read_performances,
    update_performance,
    delete_performance,
)

from api.commons.shemas import *


router = APIRouter()


@router.post("", response_model=PerformanceRead)
def create_a_performance(
    performance: PerformanceCreate, db: Session = Depends(get_session)
):
    return create_performance(performance=performance, db=db)


@router.get("", response_model=list[PerformanceRead])
def get_performances(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
):
    return read_performances(offset=offset, limit=limit, db=db)


@router.get("/{performance_id}", response_model=PerformanceRead)
def get_a_performance(performance_id: int, db: Session = Depends(get_session)):
    return read_performance(performance_id=performance_id, db=db)


@router.patch("/{performance_id}", response_model=PerformanceRead)
def update_a_performance(
    performance_id: int,
    performance: PerformanceUpdate,
    db: Session = Depends(get_session),
):
    return update_performance(
        performance_id=performance_id, performance=performance, db=db
    )


@router.delete("/{performance_id}")
def delete_a_performance(performance_id: int, db: Session = Depends(get_session)):
    return delete_performance(performance_id=performance_id, db=db)
