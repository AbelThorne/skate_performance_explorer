"""Defines a Club instance
A Club is an organization that can be associated to a Skater.
"""

from typing import Optional, Literal
from enum import Enum
from datetime import date

from pydantic import BaseModel, computed_field
from sqlmodel import SQLModel, Field, Relationship


# =================== INSCRIPTION MODELS =====================


class InscriptionBase(SQLModel):
    category: str = Field(index=True)
    skater_id: Optional[int] = Field(default=None, foreign_key="skater.id")
    competition_id: Optional[int] = Field(default=None, foreign_key="competition.id")


class Inscription(InscriptionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    skater: "Skater" = Relationship(back_populates="competition_inscriptions")
    competition: "Competition" = Relationship(back_populates="skater_inscriptions")


class InscriptionCreate(InscriptionBase):
    pass


class InscriptionRead(InscriptionBase):
    id: int


class InscriptionUpdate(SQLModel):
    category: str | None
    skater: Optional["Skater"]
    competition: Optional["Competition"]


# =================== SKATER MODELS =====================


class SkaterBase(SQLModel):
    first_name: str
    last_name: str = Field(index=True)
    birth_date: Optional[str]
    genre: str
    nation: Optional[str]
    club_id: Optional[int] = Field(default=None, foreign_key="club.id")

    @computed_field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Skater(SkaterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    club: Optional["Club"] = Relationship(back_populates="skaters")

    competition_inscriptions: list["Inscription"] = Relationship(
        back_populates="skater"
    )
    competitions: list["Competition"] = Relationship(
        back_populates="skaters",
        link_model=Inscription,
        sa_relationship_kwargs={"viewonly": True},
    )
    performances: list["Performance"] = Relationship(back_populates="skater")


class SkaterCreate(SkaterBase):
    pass


class SkaterRead(SkaterBase):
    id: int


class SkaterUpdate(SQLModel):
    first_name: str | None
    last_name: str | None
    birth_date: str | None
    genre: str | None
    nation: str | None
    club: Optional["Club"]
    competition_inscriptions: list["Inscription"] | None
    competitions: list["Competition"] | None


# =================== CLUB MODELS =====================


class ClubBase(SQLModel):
    abbrev: str = Field(index=True)
    name: str | None
    city: str | None
    nation: str | None


class Club(ClubBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    skaters: list["Skater"] = Relationship(back_populates="club")


class ClubCreate(ClubBase):
    pass


class ClubRead(ClubBase):
    id: int


class ClubUpdate(SQLModel):
    abbrev: str | None
    name: str | None
    city: str | None
    nation: str | None
    skaters: list["Skater"] | None


# =================== COMPETITION MODELS =====================


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
    links_table: Optional[str]


class Competition(CompetitionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    skaters: list["Skater"] = Relationship(
        back_populates="competitions",
        link_model=Inscription,
        sa_relationship_kwargs={"viewonly": True},
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
    skaters: list["Skater"] | None
    skater_inscriptions: list["Inscription"] | None
    performances: list["Performance"] | None


# =================== PERFORMANCE MODELS =====================
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


# =================== HEALTH MODELS =====================


class Status(str, Enum):
    OK = "OK"
    KO = "KO"


class Health(BaseModel):
    app_status: Status | None
    db_status: Status | None
    environment: Literal["development", "staging", "production"] | None


class Stats(BaseModel):
    skaters: int | None
    clubs: int | None
    competitions: int | None
    performances: int | None
