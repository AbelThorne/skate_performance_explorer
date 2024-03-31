from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .inscription import Inscription
from .competition import Competition
from .performance import Performance
from .club import Club


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
    club: "Club" = Relationship(back_populates="skaters")

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
    full_name: str | None
    first_name: str | None
    last_name: str | None
    birth_date: str | None
    genre: str | None
    nation: str | None
    club: Optional["Club"]
    competition_inscriptions: list["Inscription"] | None
    competitions: list["Competition"] | None
    performances: list["Performance"] | None
