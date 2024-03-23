from typing import Tuple, Union, Optional, List
import pdfplumber
from pdfplumber.page import Page
import pandas as pd  # type: ignore
import numpy as np
from parsers.common import EmptyResultsException, dictify, snake_case  # type: ignore


def parse_upper_table(
    page: Page,
    bbox: Tuple[
        Union[int, float], Union[int, float], Union[int, float], Union[int, float]
    ],
):
    cropped = page.crop(bbox)
    table_settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "min_words_vertical": 2,
        "snap_y_tolerance": 4,
    }
    rows = cropped.extract_table(table_settings)

    assert rows is not None
    assert len(rows) == 2
    bonification = False
    try:
        rows[1][4] = float(rows[1][4])
        rows[1][6] = float(rows[1][6])
        rows[1][7] = float(rows[1][7])
        rows[1][5] = float(rows[1][5])
    except ValueError:
        if rows[1][5][-1] == "B":
            rows[1][5] = float(rows[1][5][:-1])
            bonification = True
        else:
            raise

    # Bonification column
    rows[1].append(bonification)
    series = pd.Series(
        dict(
            zip(
                [
                    "rank",
                    "name",
                    "nation",
                    "starting_number",
                    "total_segment_score",
                    "total_element_score",
                    "total_component_score",
                    "total_deductions",
                    "bonifications",
                ],
                rows[1],
            )
        )
    )
    return series


def parse_upper_rect(page: Page, bbox: Tuple[int]):
    header_words = [
        "Rank",
        "Name",
        "Nation",
        "Starting",
        "Segment",
        "Element",
        "Program",
        "Deductions",
    ]
    cropped = page.crop(bbox)
    words = cropped.extract_words()
    v_lines = (
        [bbox[0]]
        + [
            [w for w in words if w["text"] == header][0]["x0"] - 5
            for header in header_words[1:]
        ]
        + [bbox[2]]
    )
    h_lines = [
        [w for w in words if w["text"] == "Score"][0]["bottom"] + 1,
        bbox[3],
    ]
    rows = cropped.extract_table(
        {
            "explicit_vertical_lines": v_lines,
            "explicit_horizontal_lines": h_lines,
            "vertical_strategy": "explicit",
            "horizontal_strategy": "explicit",
        }
    )
    assert len(rows) == 1
    bonification = False
    try:
        rows[0][4] = float(rows[0][4])
        rows[0][6] = float(rows[0][6])
        rows[0][7] = float(rows[0][7])
        rows[0][5] = float(rows[0][5]) if rows[0][5] != "" else 0.0
    except ValueError:
        if rows[0][5][-1] == "B":
            rows[0][5] = float(rows[0][5][:-1])
            bonification = True
        else:
            raise

    # Bonification column
    rows[0].append(bonification)
    series = pd.Series(
        dict(
            zip(
                [
                    "rank",
                    "name",
                    "nation",
                    "starting_number",
                    "total_segment_score",
                    "total_element_score",
                    "total_component_score",
                    "total_deductions",
                    "bonifications",
                ],
                rows[0],
            )
        )
    )
    return series


def parse_elements(page: Page, bbox: Tuple[int]):
    header_words = [
        "#",
        "Executed",
        "ofnI",
        "Base",
        "GOE",
        "J1",
        "J2",
        "J3",
        "J4",
        "J5",
        "J6",
        "J7",
        "J8",
        "J9",
        "Ref.",
        "Scores",
    ]
    cropped = page.crop(bbox)
    words = cropped.extract_words()
    internal_v_lines = [
        [w for w in words if w["text"] == header][0]["x0"] - 8
        for header in header_words[1:]
    ]
    v_lines = [bbox[0]] + internal_v_lines + [bbox[2]]
    # Adding column for the highlights
    v_lines = v_lines[:4] + [v_lines[4] - 20] + v_lines[4:]
    h_start = [w for w in words if w["text"] == "Elements"][0]["bottom"] + 4
    h_end = [w for w in words if w["text"] == "Components"][0]["top"] - 1
    center = cropped.crop((bbox[0], h_start, bbox[2], h_end))
    tops = [
        x[0]["top"] for x in pdfplumber.utils.cluster_objects(center.chars, "top", 0)
    ]
    h_lines = tops + [h_end]

    table_settings = {
        "explicit_vertical_lines": v_lines,
        "explicit_horizontal_lines": h_lines,
        "vertical_strategy": "explicit",
        "horizontal_strategy": "explicit",
    }
    # return table_settings
    rows = page.extract_table(table_settings)
    df = (
        pd.DataFrame(
            rows,
            columns=[
                "element_num",
                "element_desc",
                "info_flag",
                "base_value",
                "credit_flag",
                "goe",
                "J1",
                "J2",
                "J3",
                "J4",
                "J5",
                "J6",
                "J7",
                "J8",
                "J9",
                "ref",
                "scores_of_panel",
            ],
        )
        # .replace("-", np.nan)
        # .replace("", np.nan)
    )

    assert (
        df["base_value"].astype(float).pipe(lambda x: 2 * x.iloc[-1])
        - df["base_value"].astype(float).pipe(lambda x: x.sum())
    ).round(3) == 0
    panel_score = df["scores_of_panel"].astype(float).pipe(lambda x: 2 * x.iloc[-1])
    element_sum = df["scores_of_panel"].astype(float).pipe(lambda x: x.sum())
    # if not bonifications:
    #     assert (panel_score - element_sum).round(3) == 0

    for colname in ["element_num"]:
        df[colname] = df[colname].replace("-", np.nan).astype(str)
    for colname in ["element_desc", "info_flag", "credit_flag", "ref"]:
        df[colname] = df[colname].astype(str)
    for i in range(9):
        colname = "J{}".format(i + 1)
        df[colname] = df[colname].replace("", np.nan).replace("-", np.nan).astype(float)

    for colname in ["base_value", "goe", "scores_of_panel"]:
        df[colname] = df[colname].replace("", np.nan).astype(float)
    df["num"] = df["element_num"]
    df.iloc[-1, -1] = "total"
    df.set_index("num", inplace=True)

    return df, (panel_score - element_sum).round()


def parse_program_components(page: Page, bbox: Tuple[int]):
    header_words = [
        "Program",
        "Factor",
        "J1",
        "J2",
        "J3",
        "J4",
        "J5",
        "J6",
        "J7",
        "J8",
        "J9",
        "Ref.",
        "Scores",
    ]
    cropped = page.crop(bbox)
    words = cropped.extract_words()
    v_lines = (
        [bbox[0]]
        + [
            [w for w in words if w["text"] == header][0]["x0"] - 8
            for header in header_words[1:]
        ]
        + [bbox[2]]
    )
    h_start = [w for w in words if w["text"] == "Program"][0]["bottom"] + 1
    center = cropped.crop((bbox[0], h_start, bbox[2], bbox[3]))
    tops = [
        x[0]["top"] for x in pdfplumber.utils.cluster_objects(center.chars, "top", 0)
    ]
    h_lines = tops + [bbox[3]]

    table_settings = {
        "explicit_vertical_lines": v_lines,
        "explicit_horizontal_lines": h_lines,
        "vertical_strategy": "explicit",
        "horizontal_strategy": "explicit",
    }
    rows = page.extract_table(table_settings)

    df = (
        pd.DataFrame(
            rows,
            columns=[
                "component_desc",
                "factor",
                "J1",
                "J2",
                "J3",
                "J4",
                "J5",
                "J6",
                "J7",
                "J8",
                "J9",
                "ref",
                "scores_of_panel",
            ],
        )
        # .replace("-", None)
        # .replace("", None)
    )

    total_score = (
        df.iloc[:-1]
        .pipe(
            lambda x: round(
                x["scores_of_panel"].astype(float) * x["factor"].astype(float), 3
            )
        )
        .sum()
    )

    parsed_score = float(df.iloc[-1]["scores_of_panel"])
    assert total_score - parsed_score < 0.1

    df = df.iloc[:-1].copy()

    for i in range(9):
        colname = "J{}".format(i + 1)
        df[colname] = df[colname].replace("", np.nan).astype(float)

    for colname in ["factor", "scores_of_panel"]:
        df[colname] = df[colname].replace("", np.nan).replace("-", np.nan).astype(float)

    df["component"] = df["component_desc"].map(snake_case)
    df.set_index("component", inplace=True)

    return df


def parse_page(page: Page):
    tables = page.find_tables(table_settings={})

    if len(tables) == 0:
        raise EmptyResultsException
    results = []
    for t in tables:
        assert len(t.rows) == 3
        # metadata = parse_upper_rect(page, rects[i * 3]).to_dict()
        metadata = parse_upper_rect(page, t.rows[0].bbox).to_dict()
        elements, bonifications = parse_elements(page, t.rows[1].bbox)
        if bonifications != 0:
            pass
        metadata["bonifications"] = bonifications
        components = parse_program_components(page, t.rows[1].bbox)
        results.append(
            {
                "metadata": metadata,
                "elements": dictify(elements),
                "components": dictify(components),
            }
        )
    return results
