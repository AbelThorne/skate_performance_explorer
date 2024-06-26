from calendar import c
from unicodedata import category
from venv import logger
from fastapi import Depends, HTTPException, status
from numpy import full
from sqlmodel import Session, select, col
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy import func as F

from backend.database import get_session
from backend.crawler.competition_crawler import (
    get_category_results,
    get_program_detailed_results,
    get_category_entries,
    get_category_panel,
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
    segment = {
        "SP": {"details": None, "scores": None, "panel": {"URL": None, "dict": {}}},
        "FS": {"details": None, "scores": None, "panel": {}},
    }
    sp_panel_url = None
    fs_panel_url = None
    for seg in crawled["segments"]:
        if seg["name"].lower() == "short program":
            seg_name = "SP"
        elif seg["name"].lower() == "free skating":
            seg_name = "FS"
        else:
            logger.warning(f"Unknown segment {seg['name']}")
            continue
        segment[seg_name]["details"] = seg["details_link"]
        segment[seg_name]["scores"] = seg["scores_link"]
        segment[seg_name]["panel"]["URL"] = seg["officials_link"]
        segment[seg_name]["panel"]["dict"] = get_category_panel(
            segment[seg_name]["panel"]["URL"]
        )
    category_to_db = Category(
        competition=competition,
        competition_id=competition.id,
        genre=parse_category_genre(crawled["name"]),
        level=parse_category_level(crawled["name"]),
        age=parse_category_age(crawled["name"]),
        entries_url=crawled["entries_link"],
        results_url=crawled["results_link"],
        sp_detailed_results_url=segment["SP"]["details"],
        sp_panel_url=segment["SP"]["panel"]["URL"],
        sp_judge_scores=segment["SP"]["scores"],
        fs_detailed_results_url=segment["FS"]["details"],
        fs_panel_url=segment["FS"]["panel"]["URL"],
        fs_judge_scores=segment["FS"]["scores"],
    )

    ## Panels
    ############################

    for segment_obj in segment.values():
        if segment_obj["panel"]["URL"] is None:
            continue
        segment_obj["panel"]["obj"] = Panel()
        first_tech_spec = True
        for oa_func, oa in segment_obj["panel"]["dict"].items():
            match oa_func:
                case "Referee":
                    segment_obj["panel"]["obj"].referee = oa["name"]
                case "Technical Controller":
                    segment_obj["panel"]["obj"].technical_controller = oa["name"]
                case "Technical Specialist":
                    if first_tech_spec:
                        segment_obj["panel"]["obj"].technical_specialist_1 = oa["name"]
                        first_tech_spec = False
                    else:
                        segment_obj["panel"]["obj"].technical_specialist_2 = oa["name"]
                case "Data Operator":
                    segment_obj["panel"]["obj"].data_operator = oa["name"]
                case "Replay Operator":
                    segment_obj["panel"]["obj"].replay_operator = oa["name"]
                case j if j.startswith("Judge"):
                    nb = int(j[-1])
                    setattr(segment_obj["panel"]["obj"], f"judge_{nb}", oa["name"])

    if segment["SP"]["panel"]["URL"] is not None:
        category_to_db.sp_panel = segment["SP"]["panel"]["obj"]
    if segment["FS"]["panel"]["URL"] is not None:
        category_to_db.fs_panel = segment["FS"]["panel"]["obj"]

    ## Entries
    ############################
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
                    query=select(Skater).where(
                        Skater.first_name == entry["First Name"],
                        Skater.last_name == entry["Surname"],
                        Skater.club_id == club_db.id,
                    ),
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

    db.add(category_to_db)
    db.commit()
    db.refresh(category_to_db)

    ## Performances
    ############################
    if category_to_db.results_url is not None:
        df_perfs = get_category_results(category_to_db.results_url)
        if df_perfs is None:
            logger.warning(f"Could not get results for {crawled['name']}")
        else:
            performances = []
            nb_valid_entries = len(df_perfs.query("FinalRank not in ['WD', 'DSQ']"))
            for _, perf in df_perfs.iterrows():
                skater = db.exec(
                    select(Skater)
                    .where(
                        F.concat(Skater.first_name, " ", Skater.last_name)
                        == perf["Name"]
                    )
                    .where(
                        col(Skater.club_id).in_(
                            select(Club.id).where(Club.abbrev == perf["Club"])
                        )
                    )
                ).first()
                if skater is None:
                    logger.warning(
                        f"Could not find skater {perf['Name']} in the database"
                    )
                    continue
                valid_perf = perf["FinalRank"] not in ["WD", "DSQ"]
                if valid_perf:
                    performances.append(
                        Performance(
                            skater_id=skater.id,
                            skater=skater,
                            category_id=category_to_db.id,
                            category=category_to_db,
                            withdrawn=perf["FinalRank"] == "WD",
                            disqualified=perf["FinalRank"] == "DSQ",
                            rank=perf["FinalRank"],
                            score=perf["Score"],
                            total_entries=nb_valid_entries,
                        )
                    )
                else:
                    performances.append(
                        Performance(
                            skater_id=skater.id,
                            skater=skater,
                            category_id=category_to_db.id,
                            category=category_to_db,
                            withdrawn=perf["FinalRank"] == "WD",
                            disqualified=perf["FinalRank"] == "DSQ",
                            rank=None,
                            score=None,
                            total_entries=nb_valid_entries,
                        )
                    )
            db.add_all(performances)
            db.commit()

    ## Programs
    ############################
    programs = []
    performances = []
    for seg, segment_obj in segment.items():
        if segment_obj["details"] is None:
            continue
        df_progs = get_program_detailed_results(segment_obj["details"])
        if df_progs is None:
            logger.warning(
                f"Could not get detailed results for {seg} of {crawled['name']}"
            )
        else:
            for _, program in df_progs.iterrows():
                performance = db.exec(
                    select(Performance)
                    .where(
                        Performance.category_id == category_to_db.id,
                    )
                    .where(
                        col(Performance.skater_id).in_(
                            select(Skater.id)
                            .where(
                                F.concat(Skater.first_name, " ", Skater.last_name)
                                == program["Name"]
                            )
                            .where(
                                col(Skater.club_id).in_(
                                    select(Club.id).where(
                                        Club.abbrev == program["Club"]
                                    )
                                )
                            )
                        )
                    )
                ).first()
                if performance is None:
                    logger.warning(
                        f"Could not find performance of skater {program['Name']} in the database"
                    )
                    continue
                valid_prog = program["Rank"] not in ["WD", "DSQ"]
                if valid_prog:
                    program_db = Program(
                        type=seg,
                        withdrawn=program["Rank"] == "WD",
                        disqualified=program["Rank"] == "DSQ",
                        total_element_score=program["TES"],
                        total_component_score=program["PCS"],
                        total_deductions=program["Ded."],
                        total_segment_score=program["TSS"],
                        composition=program["CO"],
                        presentation=program["PR"],
                        skating_skills=program["SK"],
                        rank=program["Rank"],
                        bonifications=0.0,
                        starting_number=program["StN."],
                    )

                else:
                    program_db = Program(
                        type=seg,
                        withdrawn=program["Rank"] == "WD",
                        disqualified=program["Rank"] == "DSQ",
                        total_element_score=None,
                        total_component_score=None,
                        total_deductions=None,
                        total_segment_score=None,
                        composition=None,
                        presentation=None,
                        skating_skills=None,
                        rank=None,
                        bonifications=None,
                        starting_number=program["StN."],
                    )

                programs.append(program_db)
                performance.short_program = program_db if seg == "SP" else None
                performance.free_skating = program_db if seg == "FS" else None
                performances.append(performance)

    db.add_all(programs)
    db.add_all(performances)
    db.commit()

    db.refresh(category_to_db)
    return category_to_db
