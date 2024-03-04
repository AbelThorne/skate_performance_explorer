from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from api.database import get_session
from api.public.performance.models import (
    Performance,
    PerformanceCreate,
    PerformanceUpdate,
)


def create_performance(
    performance: PerformanceCreate, db: Session = Depends(get_session)
):
    performance_to_db = Performance.model_validate(performance)
    db.add(performance_to_db)
    db.commit()
    db.refresh(performance_to_db)
    return performance_to_db


def read_performances(
    offset: int = 0, limit: int = 20, db: Session = Depends(get_session)
):
    performances = db.exec(select(Performance).offset(offset).limit(limit)).all()
    return performances


def read_performance(performance_id: int, db: Session = Depends(get_session)):
    performance = db.get(Performance, performance_id)
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance not found with id: {performance_id}",
        )
    return performance


def update_performance(
    performance_id: int,
    performance: PerformanceUpdate,
    db: Session = Depends(get_session),
):
    performance_to_update = db.get(Performance, performance_id)
    if not performance_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance not found with id: {performance_id}",
        )

    performance_data = performance.model_dump(exclude_unset=True)
    performance_to_update.sqlmodel_update(performance_data)
    db.add(performance_to_update)
    db.commit()
    db.refresh(performance_to_update)
    return performance_to_update


def delete_performance(performance_id: int, db: Session = Depends(get_session)):
    performance = db.get(Performance, performance_id)
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance not found with id: {performance_id}",
        )

    db.delete(performance)
    db.commit()
    return {"ok": True}
