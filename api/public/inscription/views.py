from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.public.inscription.models import Inscription

router = APIRouter()
