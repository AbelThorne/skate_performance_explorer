from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .skater import Skater
    from .competition import Competition


class InscriptionBase(SQLModel):
    category: str = Field(index=True)
    skater_id: int = Field(foreign_key="skater.id")
    competition_id: int = Field(foreign_key="competition.id")


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
