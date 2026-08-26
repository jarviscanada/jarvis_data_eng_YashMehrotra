"""Deterministic cleaning shared by training notebooks and future inference code."""

import numpy as np
import pandas as pd


def clean_known_data_issues(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with known Home Credit sentinel values normalized."""
    cleaned = frame.copy()

    cleaned["DAYS_EMPLOYED_SENTINEL"] = cleaned["DAYS_EMPLOYED"].eq(365243).astype("int8")
    cleaned["DAYS_EMPLOYED"] = cleaned["DAYS_EMPLOYED"].replace(365243, np.nan)

    if "CODE_GENDER" in cleaned.columns:
        cleaned["CODE_GENDER"] = cleaned["CODE_GENDER"].replace("XNA", np.nan)

    return cleaned
