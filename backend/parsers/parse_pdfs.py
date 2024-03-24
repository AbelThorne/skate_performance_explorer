import re
from typing import Dict, Any
import pdfplumber  # type: ignore
import sys
import numpy as np
import logging
from pathlib import Path
from datetime import date
from parsers.common import EmptyResultsException  # type: ignore
from parsers.standard import parse_page as parse_standard  # type: ignore

LOGGER = logging.getLogger()


def parse_page(page, context=None):
    """
    This function takes a page object, checks whether there
    are any score sheets on the page, and the parsed out the
    structured score data from each score sheet
    """

    try:
        text = page.extract_text()

    # If pdfplumber cannot read the page, we note it in the parsing log.
    except Exception:
        LOGGER.warning(f"Cannot read page {page.page_number}")
        return None

    # For some pages -- often the graphical cover pages -- pdfplumber
    # can't find any text. We skip over those, and note them in
    # the parsing log.
    if text is None or len(text) == 0:
        LOGGER.debug(f"Cannot find text on page {page.page_number}")
        return None

    # All the score sheets should have "JUDGES DETAILS PER SKATER"
    # on the page. If a page doesn't, we continue to the next page.
    if "JUDGES DETAILS PER SKATER" not in text:
        LOGGER.debug(f"Cannot find score sheets on page {page.page_number}")
        return None

    parser = parse_standard

    try:
        parsed = parser(page)

    # A few pages of the protocol PDFs have headers that make it
    # look like they'd contain score sheets, but don't. You can
    # check the parsing log to see which these are.
    except EmptyResultsException:
        LOGGER.debug(f"Cannot find performances on page {page.page_number}")
        return None

    # If we got this far, we've been able to locate, and parse the
    # score sheets on this page.

    # Here, we extract the competition and program names,
    # and add them to the parsed data.
    if context is not None:
        header = text.split("\n")
        if header[0] == "JUDGES DETAILS PER SKATER":
            program = text.split("\n")[1]
        else:
            program = text.split("\n")[2]
        season_start = date(year=context["start"].year, month=7, day=1)
        current_year = context["start"].year
        if context["start"] > season_start:
            season = f"{current_year} - {current_year + 1}"
        else:
            season = f"{current_year- 1} - {current_year}"

        # if context is not None:
        entries = context["entries"]
        program_mask = entries.apply(
            lambda x: re.match(rf"{x.Category}.*", program, flags=re.IGNORECASE)
            != None,
            axis=1,
        )
        if len(entries[program_mask]) == 0:
            pass
        for result in parsed:
            result["metadata"]["season"] = season
            result["metadata"]["competition"] = context["competition"]
            result["metadata"]["city"] = context["city"]
            result["metadata"]["type"] = context["type"]
            result["metadata"]["start"] = context["start"]
            result["metadata"]["end"] = context["end"]
            result["metadata"]["program"] = program
            result["metadata"]["nb_entries"] = len(entries[program_mask])
            try:
                result["metadata"]["club"] = entries[
                    entries["Full name"] == result["metadata"]["name"]
                ]["Club"].values[0]
            except:
                name = result["metadata"]["name"]
                LOGGER.warning(f"Patineur introuvable dans les entrée: {name}")
                result["metadata"]["club"] = ""
            if type(result["metadata"]["club"]) != str:
                result["metadata"]["club"] = ""

    return parsed


def parse_pdf(pdf, context=None):
    """
    This function takes a PDF object, iterates through
    each page, and returns structured data representing for
    each score sheet it has found.
    """
    performances = []
    for i, page in enumerate(pdf.pages):
        parsed = parse_page(page, context)
        if parsed is None:
            continue
        performances += parsed

    for performance in performances:
        nb_entries = len(
            list(
                filter(
                    lambda x: x["metadata"]["program"]
                    == performance["metadata"]["program"],
                    performances,
                )
            )
        )
        if nb_entries != performance["metadata"]["nb_entries"]:
            performance["metadata"]["nb_entries"] = nb_entries

    return performances


def parse_pdf_from_path(path: Path, context=None) -> Dict[str, Any]:
    try:
        with pdfplumber.open(path) as pdf:
            return {"performances": parse_pdf(pdf, context), "pdf": path.name}
    except Exception as e:
        return {"exception": e.__repr__(), "pdf": path.name}
