from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.public.competition.models import Competition

router = APIRouter()
