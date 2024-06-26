from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from commons.schemas import Health, Stats
from backend.database import Session, get_session
from backend.crud.health import get_health, get_stats
from logger import logger_config


router = APIRouter()
logger = logger_config(__name__)


@router.get(
    "",
    response_model=Health,
    status_code=status.HTTP_200_OK,
    responses={200: {"model": Health}},
)
async def health(db: Session = Depends(get_session)):
    return get_health(db=db)


@router.get(
    "/stats",
    response_model=Stats,
    status_code=status.HTTP_200_OK,
    responses={200: {"model": Stats}},
)
async def health_stats(db: Session = Depends(get_session)):
    return get_stats(db=db)
