from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.public.club.models import Club

router = APIRouter()
