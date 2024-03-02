"""Defines a Competition instance
A Competition is an event that takes place at a given date and contains
performances from different categories.
"""

from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

from api.public.inscription.models import Inscription

if TYPE_CHECKING:
    from api.public.skater.models import Skater
    from api.public.performance.models import Performance


class CompetitionBase(SQLModel):
    name: str
    type: str
    season: str
    start: Optional[date]
    end: Optional[date]
    location: Optional[str]
    rink_name: Optional[str]
    url: Optional[str]
    processed: bool = False


class Competition(CompetitionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    skaters: list["Skater"] = Relationship(
        back_populates="competitions", link_model=Inscription
    )
    skater_inscriptions: list["Inscription"] = Relationship(
        back_populates="competition"
    )
    performances: list["Performance"] = Relationship(back_populates="competition")
