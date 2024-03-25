from typing import Optional, TYPE_CHECKING
from datetime import date

from sqlmodel import SQLModel, Field, Relationship

from .inscription import Inscription

if TYPE_CHECKING:
    from .skater import Skater
    from .performance import Performance


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
