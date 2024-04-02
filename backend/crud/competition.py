from typing import List
import json
import pandas as pd

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from logger import logger_config
from backend.database import get_session
from commons.schemas import *

from backend.crud.category import create_category_from_crawler
from backend.crawler.competition_crawler import get_links_table

logger = logger_config(__name__)


def create_competition(
    competition: CompetitionCreate, db: Session = Depends(get_session)
):
    competition_to_db = Competition.model_validate(competition)
    db.add(competition_to_db)
    db.commit()
    db.refresh(competition_to_db)
    return competition_to_db


def read_competitions(
    offset: int = 0, limit: int = 20, db: Session = Depends(get_session)
):
    competitions = db.exec(select(Competition).offset(offset).limit(limit)).all()
    return competitions


def read_competition(competition_id: int, db: Session = Depends(get_session)):
    competition = db.get(Competition, competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competition not found with id: {competition_id}",
        )
    return competition


def update_competition(
    competition_id: int,
    competition: CompetitionUpdate,
    db: Session = Depends(get_session),
):
    competition_to_update = db.get(Competition, competition_id)
    if not competition_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competition not found with id: {competition_id}",
        )

    competition_data = competition.model_dump(exclude_unset=True)
    competition_to_update.sqlmodel_update(competition_data)
    db.add(competition_to_update)
    db.commit()
    db.refresh(competition_to_update)
    return competition_to_update


def delete_competition(competition_id: int, db: Session = Depends(get_session)):
    competition = db.get(Competition, competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competition not found with id: {competition_id}",
        )

    db.delete(competition)
    db.commit()
    return {"ok": True}


def crawl_competition(competition_id: int, db: Session = Depends(get_session)):
    """Crawls the competition's website to get the links to the categories entries and
    the score cards. Adds the skaters to the database if they are not already there.
    """
    competition = read_competition(competition_id, db)

    # Crawls the competition's website to get the links to the categories entries and the score cards
    links_table = get_links_table(competition)
    assert links_table is not None

    for cat in links_table.values():
        create_category_from_crawler(cat, competition, db)


# def create_inscriptions(
#     entries: pd.DataFrame, competition: Competition, db: Session = Depends(get_session)
# ):
#     """Create inscriptions for a competition."""
#     inscriptions = []

#     entries["Club"] = entries["Club"].fillna("")
#     inscription = None
#     for _, row in entries.iterrows():
#         club = club_get_or_create(
#             Club(abbrev=row["Club"], name=None, city=None, nation=None), db
#         )
#         skater = skater_get_or_create(
#             Skater(
#                 first_name=row["First Name"],
#                 last_name=row["Surname"],
#                 genre=row["Genre"],
#                 nation=row["Nationality"],
#                 club=club,
#                 birth_date=None,
#             ),
#             db,
#         )
#         assert skater.id is not None
#         assert competition.id is not None
#         inscription = Inscription(
#             skater=skater, competition=competition, category=row["Category"]
#         )
#         inscriptions.append(inscription)
#     db.add_all(inscriptions)
#     db.commit()
