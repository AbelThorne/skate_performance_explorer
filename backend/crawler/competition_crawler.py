from enum import Enum
from pathlib import Path
from typing import Optional, Tuple, Any, Dict
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

    rows = table.find_all("tr")
    headers = [cell.text.strip() for cell in rows[0].find_all("th")]
    for r in rows[1:]:
        cells = r.find_all("td")
        full_name = cells[1].text.strip()
        if full_name == "":
            continue
        surname = " ".join(list(filter(lambda w: w.isupper(), full_name.split(" "))))
        first_name = " ".join(
            list(filter(lambda w: not w.isupper(), full_name.split(" ")))
        )
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

    rows = table.find_all("tr")
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
        processed=False,
        links_table=None,
    )
    links = get_links_table(comp)
