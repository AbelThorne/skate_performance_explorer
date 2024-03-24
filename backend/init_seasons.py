from sqlmodel import Session

from datetime import date

from backend.database import engine
from commons.shemas import Competition
from logger import logger_config

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
                skaters=[],
                skater_inscriptions=[],
                performances=[],
            )
        )

        for competition in competitions:
            session.add(competition)
        session.commit()
        logger.info(f"============ Created season 2023-2024 ============")
        for competition in competitions:
            session.refresh(competition)
            logger.info(
                f"Competition {competition.name} created with id {competition.id} ({competition})"
            )
