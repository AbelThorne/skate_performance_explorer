"""Defines an inscription instance
An inscription is an association between a Skater and a Competition with an
associated category.
"""

from datetime import date
from typing import TYPE_CHECKING, Literal, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from api.public.skater.models import Skater
    from api.public.competition.models import Competition


class InscriptionBase(SQLModel):
    category: str = Field(index=True)


class Inscription(InscriptionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    skater_id: int = Field(foreign_key="skater.id")
    skater: "Skater" = Relationship(back_populates="skaters")

    competition_id: int = Field(foreign_key="competition.id")
    competition: "Competition" = Relationship(back_populates="incription")
