from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from commons.schemas import *
from backend.database import get_session
from backend.crud.performance import (
    create_performance,
    read_performance,
    read_performances,
    update_performance,
    delete_performance,
)


router = APIRouter()


@router.post("", response_model=PerformanceRead)
async def create_a_performance(
    performance: PerformanceCreate, db: Session = Depends(get_session)
):
    return create_performance(performance=performance, db=db)


@router.get("", response_model=list[PerformanceRead])
async def get_performances(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
):
    return read_performances(offset=offset, limit=limit, db=db)


@router.get("/{performance_id}", response_model=PerformanceRead)
async def get_a_performance(performance_id: int, db: Session = Depends(get_session)):
    return read_performance(performance_id=performance_id, db=db)


@router.patch("/{performance_id}", response_model=PerformanceRead)
async def update_a_performance(
    performance_id: int,
    performance: PerformanceUpdate,
    db: Session = Depends(get_session),
):
    return update_performance(
        performance_id=performance_id, performance=performance, db=db
    )


@router.delete("/{performance_id}")
async def delete_a_performance(performance_id: int, db: Session = Depends(get_session)):
    return delete_performance(performance_id=performance_id, db=db)
