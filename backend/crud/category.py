from calendar import c
from unicodedata import category
from venv import logger
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from backend.database import get_session
from backend.crawler.competition_crawler import (
    get_category_entries,
    get_panel,
    parse_category_age,
    parse_category_genre,
    parse_category_level,
)
from backend.crud.skater import find_or_create_skater
from backend.crud.club import find_or_create_club

from commons.schemas import *

from logger import logger_config

logger = logger_config(__name__)


def create_category(category: CategoryCreate, db: Session = Depends(get_session)):
    category_to_db = Category.model_validate(category)
    db.add(category_to_db)
    db.commit()
    db.refresh(category_to_db)
    return category_to_db


def read_categories(
    offset: int = 0, limit: int = 20, db: Session = Depends(get_session)
):
    categories = db.exec(select(Category).offset(offset).limit(limit)).all()
    return categories


def read_category(category_id: int, db: Session = Depends(get_session)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category not found with id: {category_id}",
        )
    return category


def update_category(
    category_id: int, category: CategoryUpdate, db: Session = Depends(get_session)
):
    category_to_update = db.get(Category, category_id)
    if not category_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category not found with id: {category_id}",
        )

    category_data = category.model_dump(exclude_unset=True)
    category_to_update.sqlmodel_update(category_data)
    db.add(category_to_update)
    db.commit()
    db.refresh(category_to_update)
    return category_to_update


def delete_category(category_id: int, db: Session = Depends(get_session)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category not found with id: {category_id}",
        )

    db.delete(category)
    db.commit()


def find_or_create_category(
    query: SelectOfScalar[Category],
    category: CategoryCreate,
    db: Session = Depends(get_session),
):
    query_result = db.exec(query).first()
    if query_result:
        return query_result
    else:
        return create_category(category, db)


def create_category_from_crawler(
    crawled: dict, competition: Competition, db: Session = Depends(get_session)
) -> Category:
    assert competition.id is not None
    panels = {}
    fs_details = None
    fs_scores = None
    sp_details = None
    sp_scores = None
    sp_panel_url = None
    fs_panel_url = None
    for seg in crawled["segments"]:
        if seg["name"] == "Short Program":
            sp_details = seg["details_link"]
            sp_panel_url = seg["officials_link"]
            sp_scores = seg["scores_link"]
            panels["SP"] = {}
            panels["SP"]["dict"] = get_panel(sp_panel_url)
        elif seg["name"] == "Free Skating":
            fs_details = seg["details_link"]
            fs_panel_url = seg["officials_link"]
            fs_scores = seg["scores_link"]
            panels["FP"] = {}
            panels["FP"]["dict"] = get_panel(fs_panel_url)
    category_to_db = Category(
        competition=competition,
        competition_id=competition.id,
        genre=parse_category_genre(crawled["name"]),
        level=parse_category_level(crawled["name"]),
        age=parse_category_age(crawled["name"]),
        entries_url=crawled["entries_link"],
        results_url=crawled["results_link"],
        sp_detailed_results_url=sp_details,
        sp_panel_url=sp_panel_url,
        sp_judge_scores=sp_scores,
        fs_detailed_results_url=fs_details,
        fs_panel_url=fs_panel_url,
        fs_judge_scores=fs_scores,
    )

    for seg, panel in panels.items():
        panel["obj"] = Panel()
        first_tech_spec = True
        for oa_func, oa in panel["dict"].items():
            match oa_func:
                case "Referee":
                    panel["obj"].referee = oa["name"]
                case "Technical Controller":
                    panel["obj"].technical_controller = oa["name"]
                case "Technical Specialist":
                    if first_tech_spec:
                        panel["obj"].technical_specialist_1 = oa["name"]
                        first_tech_spec = False
                    else:
                        panel["obj"].technical_specialist_2 = oa["name"]
                case "Data Operator":
                    panel["obj"].data_operator = oa["name"]
                case "Replay Operator":
                    panel["obj"].replay_operator = oa["name"]
                case j if j.startswith("Judge"):
                    nb = int(j[-1])
                    setattr(panel["obj"], f"judge_{nb}", oa["name"])
    if "SP" in panels:
        category_to_db.sp_panel = panels["SP"]["obj"]
        category_to_db.sp_panel_id = panels["SP"]["obj"].id
    if "FP" in panels:
        category_to_db.sp_panel = panels["FP"]["obj"]

    df_entry = get_category_entries(crawled["entries_link"])
    if df_entry is None:
        logger.warning(f"Could not get entries for {crawled['name']}")
    else:
        entries = []
        for _, entry in df_entry.iterrows():
            club_db = find_or_create_club(
                query=select(Club).where(Club.abbrev == entry["Club"]),
                club=ClubCreate(abbrev=entry.Club),
                db=db,
            )

            entries.append(
                find_or_create_skater(
                    query=select(Skater).where(Skater.full_name == entry["Full name"]),
                    skater=SkaterCreate(
                        first_name=entry["First Name"],
                        last_name=entry["Surname"],
                        genre=category_to_db.genre,
                        club_id=club_db.id,
                        nation=entry["Nationality"],
                    ),
                    db=db,
                )
            )
            category_to_db.entries = entries

        # create_inscriptions(df_entry, competition, db)
    db.add(category_to_db)
    db.commit()
    db.refresh(category_to_db)
    return category_to_db
