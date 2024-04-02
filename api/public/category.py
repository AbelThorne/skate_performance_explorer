from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from commons.schemas import *
from backend.database import get_session
from backend.crud.category import (
    create_category,
    read_category,
    read_categories,
    update_category,
    delete_category,
)

router = APIRouter()


@router.post("", response_model=CategoryRead)
async def create_a_category(
    category: CategoryCreate, db: Session = Depends(get_session)
):
    return create_category(category=category, db=db)


@router.get("", response_model=list[CategoryRead])
async def get_categories(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    db: Session = Depends(get_session),
):
    return read_categories(offset=offset, limit=limit, db=db)


@router.get("/{category_id}", response_model=CategoryReadWithCompetition)
async def get_a_category(category_id: int, db: Session = Depends(get_session)):
    return read_category(category_id=category_id, db=db)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_a_category(
    category_id: int, category: CategoryUpdate, db: Session = Depends(get_session)
):
    return update_category(category_id=category_id, category=category, db=db)


@router.delete("/{category_id}")
async def delete_a_category(category_id: int, db: Session = Depends(get_session)):
    return delete_category(category_id=category_id, db=db)
