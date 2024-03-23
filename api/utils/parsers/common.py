from re import sub
import numpy as np
import pandas as pd  # type: ignore


class EmptyResultsException(Exception):
    pass


def dictify(df: pd.DataFrame) -> dict | None:
    if df is None:
        return None
    else:
        return df.to_dict(orient="index")


def snake_case(s: str) -> str:
    return "_".join(
        sub(
            "([A-Z][a-z]+)", r" \1", sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()
