"""Defines a Club instance
A Club is an organization that can be associated to a Skater.
"""

from typing import Optional, Literal
from enum import Enum
from datetime import date

from pydantic import BaseModel, computed_field
from sqlmodel import SQLModel, Field, Relationship


# =================== INSCRIPTION MODELS =====================


class Inscription(SQLModel, table=True):
    skater_id: int | None = Field(
        default=None, foreign_key="skater.id", primary_key=True
    )
    category_id: int | None = Field(
        default=None, foreign_key="category.id", primary_key=True
    )


# =================== PANEL MODELS =====================


class PanelBase(SQLModel):
    referee: str | None = None
    judge_1: str | None = None
    judge_2: str | None = None
    judge_3: str | None = None
    judge_4: str | None = None
    judge_5: str | None = None
    judge_6: str | None = None
    judge_7: str | None = None
    judge_8: str | None = None
    judge_9: str | None = None
    technical_specialist_1: str | None = None
    technical_specialist_2: str | None = None
    technical_controller: str | None = None
    data_operator: str | None = None
    replay_operator: str | None = None
    category_id: int | None = Field(default=None, foreign_key="category.id")


class Panel(PanelBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category: "Category" = Relationship()


# =================== CATEGORY MODELS =====================


class CategoryBase(SQLModel):
    genre: str
    age: str
    level: str

    entries_url: str | None = None
    sp_panel_url: str | None = None
    fs_panel_url: str | None = None
    sp_detailed_results_url: str | None = None
    fs_detailed_results_url: str | None = None
    sp_judge_scores: str | None = None
    fs_judge_scores: str | None = None
    results_url: str | None = None

    competition_id: int = Field(foreign_key="competition.id")

    @computed_field
    def name(self) -> str:
        return ""


class Category(CategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    competition: "Competition" = Relationship(back_populates="categories")
    entries: list["Skater"] = Relationship(
        back_populates="inscriptions", link_model=Inscription
    )
    performances: list["Performance"] = Relationship(back_populates="category")

    fs_panel: Optional["Panel"] = Relationship(back_populates="category")
    sp_panel: Optional["Panel"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    fs_panel: Optional["Panel"]
    sp_panel: Optional["Panel"]


class CategoryReadWithCompetition(CategoryRead):
    competition: Optional["Competition"] = None


class CategoryUpdate(SQLModel):
    # genre: Literal["Hommes", "Dames"] | None
    genre: str | None
    # age: (
    #     list[Literal["Poussin", "Benjamin", "Minime", "Novice", "Junior", "Senior"]]
    #     | None
    # )
    age: str | None
    # level: (
    #     Literal[
    #         "Duo",
    #         "Exhibition",
    #         "Open",
    #         "Adulte Acier",
    #         "Adulte Etain",
    #         "Adulte Bronze",
    #         "Adulte Argent",
    #         "Adulte Or",
    #         "Adulte Masters",
    #         "R3 D",
    #         "R3 C",
    #         "R3 B",
    #         "R3 A",
    #         "R2",
    #         "R1",
    #         "Federal",
    #         "National",
    #         "International",
    #     ]
    #     | None
    # )
    level: str | None
    entries_url: str | None
    sp_panel_url: str | None
    fs_panel_url: str | None
    sp_detailed_results_url: str | None
    fs_detailed_results_url: str | None
    sp_judge_scores: str | None
    fs_judge_scores: str | None
    results_url: str | None
    referee: str | None
    judge_1: str | None
    judge_2: str | None
    judge_3: str | None
    judge_4: str | None
    judge_5: str | None
    judge_6: str | None
    judge_7: str | None
    judge_8: str | None
    judge_9: str | None
    technical_specialist_1: str | None
    technical_specialist_2: str | None
    technical_controller: str | None
    data_operator: str | None
    replay_operator: str | None
    competition: Optional["Competition"] | None
    entries: list["Skater"] | None
    performances: list["Performance"] | None
    fs_panel: Optional["Panel"] | None
    sp_panel: Optional["Panel"] | None


# =================== SKATER MODELS =====================


class SkaterBase(SQLModel):
    first_name: str
    last_name: str = Field(index=True)
    birth_date: Optional[str] = None
    genre: str
    nation: Optional[str]
    club_id: Optional[int] = Field(default=None, foreign_key="club.id")


class Skater(SkaterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    club: Optional["Club"] = Relationship(back_populates="skaters")

    inscriptions: list["Category"] = Relationship(
        back_populates="entries", link_model=Inscription
    )
    performances: list["Performance"] = Relationship(back_populates="skater")


class SkaterCreate(SkaterBase):
    pass


class SkaterRead(SkaterBase):
    id: int


class SkaterReadWithClub(SkaterRead):
    club: Optional["Club"] = None


class SkaterUpdate(SQLModel):
    first_name: str | None
    last_name: str | None
    birth_date: str | None
    genre: str | None
    nation: str | None
    club: Optional["Club"]
    inscriptions: list["Category"] | None
    competitions: list["Competition"] | None
    performances: list["Performance"] | None


# =================== CLUB MODELS =====================


class ClubBase(SQLModel):
    abbrev: str = Field(index=True)
    name: str | None = None
    city: str | None = None
    nation: str | None = None


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
    circuit: Optional[str] = None
    url: Optional[str]


class Competition(CompetitionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    categories: list["Category"] = Relationship(back_populates="competition")


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
    circuit: str | None
    url: str | None
    categories: list["Category"] | None


# =================== PERFORMANCE MODELS =====================
class PerformanceBase(SQLModel):
    skater_id: int | None = Field(default=None, foreign_key="skater.id")
    category_id: int | None = Field(default=None, foreign_key="category.id")
    segment: str | None
    rank: int | None
    withdrawn: bool | None = False
    disqualified: bool | None = False
    starting_number: int
    total_segment_score: float | None
    total_element_score: float | None
    total_component_score: float | None
    total_deductions: float | None
    composition: float | None
    presentation: float | None
    skating_skills: float | None
    bonifications: float | None
    total_entries: int


class Performance(PerformanceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    skater: "Skater" = Relationship(back_populates="performances")
    category: "Category" = Relationship(back_populates="performances")


class PerformanceCreate(PerformanceBase):
    pass


class PerformanceRead(PerformanceBase):
    id: int


class PerformanceUpdate(SQLModel):
    skater: Optional["Skater"]
    category: Optional["Category"]
    segment: str | None
    rank: int | None
    withdrawn: bool | None
    starting_number: int | None
    total_segment_score: float | None
    total_element_score: float | None
    total_component_score: float | None
    total_deductions: float | None
    composition: float | None
    presentation: float | None
    skating_skills: float | None
    bonifications: float | None
    total_entries: int | None = None


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
