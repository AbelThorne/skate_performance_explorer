"""Defines a Competition instance
A Competition is an event that takes place at a given date and contains
performances from different categories.
"""

from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

from api.public.inscription.models import Inscription
from api.public.performance.models import Performance

if TYPE_CHECKING:
    from api.public.skater.models import Skater


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


class CompetitionCreate(CompetitionBase):
    pass


class CompetitionRead(CompetitionBase):
    id: int


class CompetitionUpdate(SQLModel):
    name: str | None
    type: str | None
    season: str | None
    start: date | None
    end: date | None
    location: str | None
    rink_name: str | None
    url: str | None
    processed: bool | None
    # skaters: list[Skater] | None
    # skater_inscriptions: list[Inscription] | None
    # performances: list[Performance] | None
