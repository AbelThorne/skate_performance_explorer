from backend.database import engine
from sqlmodel import select, col
from commons.schemas import *


## Get all skaters from a given club
def query_skaters_from_club(club_name: str, id_only: bool = False):
    query = select(Skater if not id_only else Skater.id).where(
        col(Skater.club_id).in_(select(Club.id).where(Club.abbrev == club_name))
    )
    return query


## Get all competitions where a given club was present
def query_competitions_from_club(club_name: str, id_only: bool = False):
    query = select(Competition if not id_only else Competition.id).where(
        col(Competition.id).in_(
            select(Category.competition_id).where(
                col(Category.id).in_(
                    select(Performance.category_id).where(
                        col(Performance.skater_id).in_(
                            query_skaters_from_club(club_name, id_only=True)
                        )
                    )
                )
            )
        )
    )
    return query


## Get all performances from a given competition
def query_performances_from_competition(competition_id: int, id_only: bool = False):
    query = select(Performance if not id_only else Performance.id).where(
        col(Performance.category_id).in_(
            select(Category.id).where(col(Category.competition_id) == competition_id)
        )
    )
    return query
