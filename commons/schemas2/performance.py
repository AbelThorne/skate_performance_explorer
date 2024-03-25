from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .competition import Competition
    from .skater import Skater


class PerformanceBase(SQLModel):
    skater_id: int = Field(foreign_key="skater.id")
    competition_id: int = Field(foreign_key="competition.id")
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

    skater: "Skater" = Relationship(back_populates="performances")
    competition: "Competition" = Relationship(back_populates="performances")


class PerformanceCreate(PerformanceBase):
    pass


class PerformanceRead(PerformanceBase):
    id: int


class PerformanceUpdate(SQLModel):
    skater: Optional["Skater"]
    competition: Optional["Competition"]
    category: str | None
    score: float | None
    rank: int | None
    nb_entries: int | None
    starting_number: int | None
    total_segment_score: float | None
    total_element_score: float | None
    total_component_score: float | None
    total_deductions: float | None
    bonifications: float | None
    program: str | None
