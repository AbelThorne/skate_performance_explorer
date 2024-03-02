"""Defines a Club instance
A Club is an organization that can be associated to a Skater.
"""

from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from api.public.skater.models import Skater


class ClubBase(SQLModel):
    name: str = Field(index=True)
    city: str | None
    nation: str | None


class Club(ClubBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    skaters: list["Skater"] = Relationship(back_populates="club")
