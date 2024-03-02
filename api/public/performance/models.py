"""Defines a Performance instance
A Performance is a result of a Skater in a given Competition.
"""

from datetime import date
from typing import TYPE_CHECKING, Literal, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from api.public.skater.models import Skater
    from api.public.competition.models import Competition


class PerformanceBase(SQLModel):
    category: str = Field(index=True)
    score: float
    rank: int
    nb_entries: int
    starting_number: int
    total_segment_score: float
    total_element_score: float
    total_component_score: float
    total_deductions: float
    bonifications: float
    program: str


class Performance(PerformanceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    skater_id: int = Field(foreign_key="skater.id")
    skater: "Skater" = Relationship(back_populates="performances")

    competition_id: int = Field(foreign_key="competition.id")
    competition: "Competition" = Relationship(back_populates="performances")
