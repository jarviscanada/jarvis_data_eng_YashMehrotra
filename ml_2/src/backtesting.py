"""Small, transparent helpers for long-or-cash portfolio backtests."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def run_long_cash_backtest(
    predictions: pd.DataFrame,
    *,
    date_col: str = "Date",
    asset_col: str = "Ticker",
    prediction_col: str = "prediction",
    return_col: str = "actual_return",
    transaction_cost_bps: float = 10.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Backtest an equal-weight long-or-cash strategy.

    Each asset is long when its prediction is positive and otherwise held in
    cash. A cost is charged whenever the asset-level position changes. The
    function returns asset-level rows and a daily equal-weight portfolio.
    """

    required = {date_col, asset_col, prediction_col, return_col}
    missing = required.difference(predictions.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    rows = predictions[list(required)].copy()
    rows[date_col] = pd.to_datetime(rows[date_col])
    rows = rows.dropna().sort_values([asset_col, date_col]).reset_index(drop=True)
    if rows.empty:
        raise ValueError("No complete prediction rows were supplied.")

    rows["position"] = (rows[prediction_col] > 0).astype(float)
    previous = rows.groupby(asset_col)["position"].shift(fill_value=0.0)
    rows["trade"] = (rows["position"] - previous).abs()
    rows["gross_return"] = rows["position"] * rows[return_col]
    rows["cost"] = rows["trade"] * (transaction_cost_bps / 10_000)
    rows["net_return"] = rows["gross_return"] - rows["cost"]

    daily = (
        rows.groupby(date_col, as_index=False)
        .agg(
            gross_return=("gross_return", "mean"),
            net_return=("net_return", "mean"),
            turnover=("trade", "mean"),
            active_positions=("position", "sum"),
        )
        .sort_values(date_col)
    )
    daily["equity"] = np.exp(daily["net_return"].cumsum())
    daily["gross_equity"] = np.exp(daily["gross_return"].cumsum())
    daily["running_peak"] = daily["equity"].cummax()
    daily["drawdown"] = daily["equity"] / daily["running_peak"] - 1
    return rows, daily


def performance_metrics(
    daily: pd.DataFrame,
    *,
    return_col: str = "net_return",
    initial_capital: float = 1_000_000.0,
) -> dict[str, float]:
    """Return common risk and business metrics for daily log returns."""

    returns = daily[return_col].dropna().astype(float)
    if returns.empty:
        raise ValueError("The daily return series is empty.")

    years = len(returns) / TRADING_DAYS
    total_return = float(np.exp(returns.sum()) - 1)
    annualized_return = float(np.exp(returns.sum() / years) - 1)
    annualized_volatility = float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS))
    sharpe = (
        float(returns.mean() / returns.std(ddof=1) * np.sqrt(TRADING_DAYS))
        if returns.std(ddof=1) > 0
        else np.nan
    )

    equity = np.exp(returns.cumsum())
    max_drawdown = float((equity / equity.cummax() - 1).min())
    final_value = initial_capital * (1 + total_return)

    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
        "final_value": float(final_value),
        "dollar_pnl": float(final_value - initial_capital),
        "trading_days": int(len(returns)),
    }


def monthly_returns(daily: pd.DataFrame, *, date_col: str = "Date") -> pd.Series:
    """Compound daily log returns into calendar-month simple returns."""

    series = daily.set_index(pd.to_datetime(daily[date_col]))["net_return"]
    return series.resample("ME").sum().pipe(np.exp).sub(1).rename("return")
