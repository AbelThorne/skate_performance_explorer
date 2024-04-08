import os
import yaml
from sqlmodel import Session, select

from backend.database import engine
from commons.schemas import Competition
from backend.crud.competition import crawl_competition
from logger import logger_config
from backend.database import drop_db_and_tables, create_db_and_tables

from commons.schemas import *

logger = logger_config(__name__)


def initialize_competitions(rebuild_all: bool = False):
    """Initialize the database with the competitions listed in the 'competitions' folder. Each season is a YAML file where
    competitions are listed in the following format:
    ```
        season: 2023-2024
        circuits:
          - name: Ligue Occitanie
            competitions:
              - name: "Competition name"
                season: "2023-2024"
                type: "TF"
                start: "2023-12-02"
                end: "2023-12-03"
                location: "Font Romeu"
                rink_name: "Patinoire Philippe Candeloro"
                url: "http://isujs.so.free.fr/Resultats/Resultats-2023-2024/TF-PRIDO/index.htm"
    ```
    """

    if rebuild_all:
        drop_db_and_tables()
        create_db_and_tables()
    with Session(engine) as session:
        for season in os.listdir("competitions"):
            if season.endswith(".yaml"):
                with open(f"competitions/{season}", "r") as file:
                    season_data = yaml.safe_load(file)
                    season_name = season_data["season"]
                    circuits = season_data["circuits"]
                    for circuit in circuits:
                        for competition in circuit["competitions"]:
                            comp_db = session.exec(
                                select(Competition).where(
                                    Competition.name == competition["name"],
                                    Competition.season == season_name,
                                )
                            ).first()
                            if comp_db:
                                logger.info(
                                    f"Competition {competition['name']} already exists with id {comp_db.id}"
                                )
                            else:
                                competition["season"] = season_name
                                competition["circuit"] = circuit["name"]
                                comp = Competition(**competition)
                                session.add(comp)
                                session.commit()
                                session.refresh(comp)
                                assert comp.id is not None
                                crawl_competition(comp.id, session)
                                logger.info(
                                    f"Competition {comp.name} created with id {comp.id} ({comp})"
                                )


if __name__ == "__main__":
    initialize_competitions(rebuild_all=False)
