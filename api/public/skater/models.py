"""Defines a Skater instance
A Skater is a physical person who participated in at least one Competition.
For each Competition a Skater participated to, a got a Performance. A Skater is
also associated to a Club.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship

from api.public.club.models import Club
from api.public.competition.models import Competition
from api.public.inscription.models import Inscription


class SkaterBase(SQLModel):
    full_name: str = Field(index=True)
    first_name: str
    last_name: str = Field(index=True)
    birth_date: str
    genre: str
    nation: Optional[str]


class Skater(SkaterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    club_id: int = Field(foreign_key="club.id")
    club: "Club" = Relationship(back_populates="skater")

    competition_inscriptions: list["Inscription"] = Relationship(
        back_populates="skater"
    )
    competitions: list["Competition"] = Relationship(
        back_populates="skaters", link_model=Inscription
    )


class SkaterCreate(SkaterBase):
    pass


class SkaterRead(SkaterBase):
    id: int


class SkaterUpdate(SQLModel):
    full_name: str | None
    first_name: str | None
    last_name: str | None
    birth_date: str | None
    genre: str | None
    nation: str | None
    club: Optional["Club"]
    competition_inscriptions: list["Inscription"] | None
    competitions: list["Competition"] | None
