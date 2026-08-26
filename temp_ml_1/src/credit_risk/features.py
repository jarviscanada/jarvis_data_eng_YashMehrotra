"""Feature transformations shared by model training and inference."""

import numpy as np
import pandas as pd


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace(0, np.nan)
    result = numerator / denominator
    return result.replace([np.inf, -np.inf], np.nan)


def engineer_application_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add deterministic application-level features to a copy of ``frame``."""
    out = frame.copy()

    out["AGE_YEARS"] = -out["DAYS_BIRTH"] / 365.25
    out["EMPLOYMENT_YEARS"] = -out["DAYS_EMPLOYED"] / 365.25

    out["CREDIT_INCOME_RATIO"] = _safe_divide(out["AMT_CREDIT"], out["AMT_INCOME_TOTAL"])
    out["ANNUITY_INCOME_RATIO"] = _safe_divide(out["AMT_ANNUITY"], out["AMT_INCOME_TOTAL"])
    out["CREDIT_TERM_PROXY"] = _safe_divide(out["AMT_ANNUITY"], out["AMT_CREDIT"])
    out["EMPLOYMENT_AGE_RATIO"] = _safe_divide(out["EMPLOYMENT_YEARS"], out["AGE_YEARS"])
    out["INCOME_PER_PERSON"] = _safe_divide(out["AMT_INCOME_TOTAL"], out["CNT_FAM_MEMBERS"])
    out["CREDIT_GOODS_RATIO"] = _safe_divide(out["AMT_CREDIT"], out["AMT_GOODS_PRICE"])
    out["ANNUITY_CREDIT_RATIO"] = _safe_divide(out["AMT_ANNUITY"], out["AMT_CREDIT"])

    ext_cols = ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
    out["EXT_SOURCE_MEAN"] = out[ext_cols].mean(axis=1)
    out["EXT_SOURCE_STD"] = out[ext_cols].std(axis=1)
    out["EXT_SOURCE_MIN"] = out[ext_cols].min(axis=1)
    out["EXT_SOURCE_MAX"] = out[ext_cols].max(axis=1)
    out["EXT_SOURCE_MISSING_COUNT"] = out[ext_cols].isna().sum(axis=1).astype("int8")

    out["AGE_BUCKET"] = pd.cut(
        out["AGE_YEARS"],
        bins=[20, 30, 40, 50, 60, 70, 100],
        labels=["20-29", "30-39", "40-49", "50-59", "60-69", "70+"],
        include_lowest=True,
    )

    document_cols = [column for column in out.columns if column.startswith("FLAG_DOCUMENT_")]
    contact_cols = ["FLAG_MOBIL", "FLAG_WORK_PHONE", "FLAG_CONT_MOBILE", "FLAG_PHONE", "FLAG_EMAIL"]
    out["DOCUMENT_COUNT"] = out[document_cols].sum(axis=1)
    out["CONTACTABILITY_SCORE"] = out[contact_cols].sum(axis=1)

    return out


def aggregate_bureau(bureau_frame: pd.DataFrame) -> pd.DataFrame:
    """Build one row of bureau-history features per applicant."""
    bureau_work = bureau_frame.copy()
    bureau_work["BUREAU_IS_ACTIVE"] = bureau_work["CREDIT_ACTIVE"].eq("Active").astype("int8")
    bureau_work["BUREAU_IS_CLOSED"] = bureau_work["CREDIT_ACTIVE"].eq("Closed").astype("int8")
    bureau_work["BUREAU_HAS_OVERDUE"] = (
        bureau_work["AMT_CREDIT_SUM_OVERDUE"].fillna(0).gt(0).astype("int8")
    )

    aggregated = bureau_work.groupby("SK_ID_CURR").agg(
        BUREAU_RECORD_COUNT=("SK_ID_BUREAU", "count"),
        BUREAU_ACTIVE_COUNT=("BUREAU_IS_ACTIVE", "sum"),
        BUREAU_CLOSED_COUNT=("BUREAU_IS_CLOSED", "sum"),
        BUREAU_OVERDUE_RECORD_COUNT=("BUREAU_HAS_OVERDUE", "sum"),
        BUREAU_DAYS_CREDIT_MEAN=("DAYS_CREDIT", "mean"),
        BUREAU_DAYS_CREDIT_MIN=("DAYS_CREDIT", "min"),
        BUREAU_CREDIT_SUM_MEAN=("AMT_CREDIT_SUM", "mean"),
        BUREAU_CREDIT_SUM_TOTAL=("AMT_CREDIT_SUM", "sum"),
        BUREAU_DEBT_TOTAL=("AMT_CREDIT_SUM_DEBT", "sum"),
        BUREAU_OVERDUE_MAX=("AMT_CREDIT_SUM_OVERDUE", "max"),
        BUREAU_DAYS_OVERDUE_MAX=("CREDIT_DAY_OVERDUE", "max"),
        BUREAU_PROLONG_COUNT=("CNT_CREDIT_PROLONG", "sum"),
    )

    aggregated["BUREAU_ACTIVE_RATIO"] = _safe_divide(
        aggregated["BUREAU_ACTIVE_COUNT"], aggregated["BUREAU_RECORD_COUNT"]
    )
    aggregated["BUREAU_DEBT_CREDIT_RATIO"] = _safe_divide(
        aggregated["BUREAU_DEBT_TOTAL"], aggregated["BUREAU_CREDIT_SUM_TOTAL"]
    )
    return aggregated.reset_index()
