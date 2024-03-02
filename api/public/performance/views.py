from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.public.performance.models import Performance

router = APIRouter()
