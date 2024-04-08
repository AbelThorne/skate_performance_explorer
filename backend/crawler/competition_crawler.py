from enum import Enum
from operator import ge
from pathlib import Path
from typing import Optional, Tuple, Any, Dict, Literal
import yaml  # type: ignore
import json
from datetime import datetime, date
from logger import logger_config
import re

from urllib.parse import urljoin, urlparse
import requests  # type: ignore
from bs4 import BeautifulSoup, ResultSet  # type: ignore
from dateutil.parser import parse as date_parse
from datetime import date

import pandas as pd  # type: ignore

from commons.schemas import Competition

log = logger_config(__name__)


def is_valid(url):
    """Check if a URL is valid."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_soup(url: str) -> BeautifulSoup | None:
    """Get the BeautifulSoup object for an URL

    :param url: URL to crawl
    :type url: str
    :return: BeautifulSoup object for the URL
    :rtype: BeautifulSoup | None
    """
    if not is_valid(url):
        log.error(f"Invalid URL: {url}")
        return None
    resp = requests.get(url)
    if resp.ok:
        return BeautifulSoup(resp.content, "html.parser")
    else:
        log.error(f"Error {resp.status_code} when trying to crawl {url}")
        return None


def get_category_entries(url: str) -> Optional[pd.DataFrame]:
    """Get the entries for a given category."""
    soup = get_soup(url)
    if soup is None:
        return None

    df = pd.DataFrame(
        columns=["Surname", "First Name", "Full name", "Club", "Nationality"]
    )
    table = None
    header = "\n\nNo."
    tables = soup.find_all("table")
    while len(tables) > 0 and table is None:
        t = tables.pop(0)
        if t.text.startswith(header):
            table = t

    if table is None:
        log.warning("Could not find entries table")
        return None

    rows = table.find_all("tr")  # type: ignore
    headers = [cell.text.strip() for cell in rows[0].find_all("th")]
    for r in rows[1:]:
        cells = r.find_all("td")
        full_name = " ".join(
            filter(lambda w: w != "", cells[1].text.strip().split(" "))
        )  # Remove double spaces
        if full_name == "":
            continue
        surname = " ".join(
            list(filter(lambda w: w.isupper(), full_name.split(" ")))
        ).strip()
        first_name = " ".join(
            list(filter(lambda w: not w.isupper(), full_name.split(" ")))
        ).strip()
        if "Club" in headers:
            club = cells[2].text.strip()
            nationality = cells[3].text.strip()
        else:
            club = ""
            nationality = cells[2].text.strip()
        df.loc[len(df.index)] = [  # type: ignore
            surname,
            first_name,
            full_name,
            club,
            nationality,
        ]
    return df


def get_category_panel(url: str) -> Optional[dict]:
    """Get the panel for a given category."""
    soup = get_soup(url)
    if soup is None:
        return None

    res = {}
    table = None
    header = "\n\nFunction"
    tables = soup.find_all("table")
    while len(tables) > 0 and table is None:
        t = tables.pop(0)
        if t.text.startswith(header):
            table = t
    if table is None:
        log.warning("Could not find entries table")
        return None

    rows = table.find_all("tr")  # type: ignore
    # headers = [cell.text.strip() for cell in rows[0].find_all("th")]
    for r in rows[1:]:
        cells = r.find_all("td")
        function = cells[0].text.strip()
        if function == "":
            continue
        name = cells[1].text.strip()
        nationality = cells[2].text.strip()
        res[function] = {"name": name, "nationality": nationality}
    return res


def get_category_results(url: str) -> Optional[pd.DataFrame]:
    soup = get_soup(url)
    if soup is None:
        return None

    df = pd.DataFrame(columns=["FinalRank", "Name", "Club", "Nation", "Score"])
    table = None
    header = "\n\nFPl."
    tables = soup.find_all("table")
    while len(tables) > 0 and table is None:
        t = tables.pop(0)
        if t.text.startswith(header):
            table = t

    if table is None:
        log.warning("Could not find results table")
        return None

    rows = table.find_all("tr")  # type: ignore
    for r in rows[1:]:
        cells = r.find_all("td")
        if len(cells) < 8:
            continue
        final_rank = cells[0].text.strip()
        name = " ".join(
            filter(lambda w: w != "", cells[1].text.strip().split(" "))
        )  # Remove double spaces
        club = cells[2].text.strip()
        nation = cells[6].text.strip()
        if final_rank in ["WD", "DSQ"]:
            score = 0.0
        else:
            score = float(cells[7].text.strip())
        df.loc[len(df.index)] = [  # type: ignore
            final_rank,
            name,
            club,
            nation,
            score,
        ]
    return df


def get_program_detailed_results(url: str) -> Optional[pd.DataFrame]:
    """Get the detailed results for a given category."""
    soup = get_soup(url)
    if soup is None:
        return None

    df = pd.DataFrame(
        columns=[
            "Rank",
            "Name",
            "Club",
            "Nation",
            "TSS",
            "TES",
            "PCS",
            "CO",
            "PR",
            "SK",
            "Ded.",
            "StN.",
        ]
    )
    table = None
    header = "\n\n \xa0 Pl."
    tables = soup.find_all("table")
    while len(tables) > 0 and table is None:
        t = tables.pop(0)
        if t.text.startswith(header):
            table = t

    if table is None:
        log.warning("Could not find detailed results table")
        return None

    rows = table.find_all("tr")  # type: ignore
    for r in rows[1:]:
        cells = r.find_all("td")
        if len(cells) == 0:
            continue
        rank = cells[0].text.strip()
        name = name = " ".join(
            filter(lambda w: w != "", cells[1].text.strip().split(" "))
        )  # Remove double spaces
        club = cells[2].text.strip()
        nation = cells[3].text.strip()
        if rank in ["WD", "DSQ"]:
            tss: float = 0.0
            tes: float = 0.0
            pcs: float = 0.0
            co: float = 0.0
            pr: float = 0.0
            sk: float = 0.0
            ded: float = 0.0
            stn: int = 0
        else:
            tss: float = float(cells[4].text.strip())
            tes: float = float(cells[5].text.strip())
            pcs: float = float(cells[7].text.strip())
            co: float = float(cells[8].text.strip())
            pr: float = float(cells[9].text.strip())
            sk: float = float(cells[10].text.strip())
            ded: float = float(cells[11].text.strip())
        stn: int = int(cells[12].text.strip()[1:])
        df.loc[len(df.index)] = [
            rank,
            name,
            club,
            nation,
            tss,
            tes,
            pcs,
            co,
            pr,
            sk,
            ded,
            stn,
        ]
    return df


def get_links_table(competition: Competition) -> Optional[Dict[str, Any]]:
    """Crawl the competition website to get the links to the categories entries and the score cards"""
    assert competition.url is not None
    soup = get_soup(competition.url)
    if soup is None:
        return None
    log.debug(f"Collecting links...")

    links_table = {}  # type: dict[str, Any]
    table = None
    header = "\n\nCategory"
    tables = soup.find_all("table")
    while len(tables) > 0 and table is None:
        t = tables.pop(0)
        if t.text.startswith(header):
            table = t

    if table is None:
        log.warning("Could not find master table")
        return None

    rows = table.find_all("tr")  # type: ignore
    rows = rows[1:]  # removing headers
    index = 0
    category = None
    segment = None
    while index < len(rows):
        cells = rows[index].find_all("td")
        if cells[0].text != "":
            # Each category is on several rows (at least 2): first row then one row per segment.
            # The first cell of the segment rows is empty so if the first cell is not empty, it's a new category
            if category is not None:
                # Add the previous category to the master table
                links_table[category["name"]] = category
            category = {}  # type: ignore
            category["segments"] = []
            category["name"] = cells[0].text
            category["entries_link"] = urljoin(
                competition.url, cells[2].find("a").attrs.get("href")
            )
            category["results_link"] = urljoin(
                competition.url, cells[3].find("a").attrs.get("href")
            )
        else:  # Going through the category segments
            segment = {}  # New segment
            segment["name"] = cells[1].text
            segment["officials_link"] = urljoin(
                competition.url, cells[2].find("a").attrs.get("href")
            )
            segment["details_link"] = urljoin(
                competition.url, cells[3].find("a").attrs.get("href")
            )
            if (
                len(cells) >= 5
            ):  # Sometimes there are no score cards (for some challenges)
                try:
                    segment["scores_link"] = urljoin(
                        competition.url, cells[4].find("a").attrs.get("href")
                    )
                except:  # Link can be omitted if the category is empty or if all skaters were forfeit
                    pass
            if category is not None:
                category["segments"].append(segment)
        index += 1
    # Last category is not yet added to the table
    if category is not None:
        links_table[category["name"]] = category

    return links_table


def parse_category_age(
    name: str,
) -> str:
    """Get the age category from the category name"""
    res = []
    for age in ["Poussin", "Benjamin", "Minime", "Novice", "Junior", "Senior"]:
        regex = re.compile(f"{age}|((^|\\-|/| ){age[0:3]}($|\\-|/| ))", re.IGNORECASE)
        if regex.search(name):
            res.append(age)

    return "-".join(res)


def parse_category_level(
    name: str,
) -> str:
    """Get the level from the category name"""
    for level in [
        "R3 D",
        "R3 C",
        "R3 B",
        "R3 A",
        "R2",
        "R1",
        "Fédéral",
        "F1",
        "F2",
        "National",
        "N1",
        "N2",
        "Catégorie 1",
        "Catégorie 2",
        "Catégorie 3",
        "Catégorie 4",
        "Duo",
        "Exhibition",
        "Open",
        "Adulte Acier",
        "Adulte Etain",
        "Adulte Bronze",
        "Adulte Argent",
        "Adulte Or",
        "Adulte Masters",
        "D1",
        "D2",
        "D3",
    ]:
        regex = re.compile(f"{level}", re.IGNORECASE)
        if regex.match(name):
            return level  # type: ignore

    return "International"


def parse_category_genre(name: str) -> str:
    """Get the genre from the category name"""
    genre = ""
    match name.split(" ")[-1]:
        case "Messieurs" | "Homme" | "Men" | "Garçon" | "garçon" | "Garçons":
            genre = "Hommes"
        case "Dames" | "Femme" | "Women" | "Fille" | "fille" | "Filles":
            genre = "Dames"
        case "Pairs" | "Danse" | "Couple":
            genre = "Couples"
        case _:
            log.warning(
                f"Could not find genre for category {name}, using 'Dames' as default"
            )
            genre = "Dames"
    return genre


if __name__ == "__main__":
    comp = Competition(
        name="Coupe Gerard Prido",
        season="2023-2024",
        type="TF",
        start=date(2023, 12, 2),
        end=date(2023, 12, 3),
        location="Font Romeu",
        rink_name="Patinoire Philippe Candeloro",
        url="http://isujs.so.free.fr/Resultats/Resultats-2023-2024/TF-PRIDO/index.htm",
    )
    links = get_links_table(comp)
