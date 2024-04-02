from pandas import Categorical
from sqlmodel import Session

from datetime import date

from backend.database import engine
from commons.schemas import Competition
from backend.crud.competition import crawl_competition
from logger import logger_config
from backend.database import drop_db_and_tables

from commons.schemas import *

logger = logger_config(__name__)


def create_season_2023_2024():
    with Session(engine) as session:
        competitions = []

        competitions.append(
            Competition(
                name="Coupe Gerard Prido",
                season="2023-2024",
                type="TF",
                start=date(2023, 12, 2),
                end=date(2023, 12, 3),
                location="Font Romeu",
                rink_name="Patinoire Philippe Candeloro",
                url="http://isujs.so.free.fr/Resultats/Resultats-2023-2024/TF-PRIDO/index.htm",
            )
        )

        for competition in competitions:
            session.add(competition)
        session.commit()
        logger.info(f"============ Created season 2023-2024 ============")
        for competition in competitions:
            session.refresh(competition)
            crawl_competition(competition.id, session)
            logger.info(
                f"Competition {competition.name} created with id {competition.id} ({competition})"
            )


if __name__ == "__main__":
    create_season_2023_2024()
