from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .skater import Skater


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
