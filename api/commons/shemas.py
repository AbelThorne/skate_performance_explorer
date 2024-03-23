"""Defines a Club instance
A Club is an organization that can be associated to a Skater.
"""

from typing import Optional
from datetime import date

from sqlmodel import SQLModel, Field, Relationship


class InscriptionBase(SQLModel):
    category: str = Field(index=True)
    skater_id: int = Field(foreign_key="skater.id")
    competition_id: int = Field(foreign_key="competition.id")


class Inscription(InscriptionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    skater: "Skater" = Relationship(back_populates="skaters")
    competition: "Competition" = Relationship(back_populates="incription")


class InscriptionCreate(InscriptionBase):
    pass


class InscriptionRead(InscriptionBase):
    id: int


class InscriptionUpdate(SQLModel):
    category: str | None
    skater: Optional["Skater"]
    competition: Optional["Competition"]


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


class ClubBase(SQLModel):
    name: str = Field(index=True)
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
    name: str | None
    city: str | None
    nation: str | None
    skaters: list["Skater"] | None


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
    skaters: list["Skater"] | None
    skater_inscriptions: list["Inscription"] | None
    performances: list["Performance"] | None


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
