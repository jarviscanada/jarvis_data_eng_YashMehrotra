"""Leakage-safe feature engineering shared by training and inference."""

from __future__ import annotations

import numpy as np
import pandas as pd
import ta


FEATURE_COLUMNS = [
    "LogReturn",
    "SMA_5_20_diff",
    "SMA_50_200_diff",
    "RSI",
    "MACD",
    "MACD_Signal",
    "MACD_Histogram",
    "BB_width",
    "BB_pct",
    "ATR_pct",
    "OBV_z",
    "VIX_Close",
]

REQUIRED_PRICE_COLUMNS = {"Date", "Ticker", "Close", "High", "Low", "Volume"}
MINIMUM_HISTORY_ROWS = 200


def _add_indicators(stock: pd.DataFrame) -> pd.DataFrame:
    """Create trailing indicators for one ticker without future information."""
    stock = stock.sort_values("Date").copy()
    close = stock["Close"]
    high = stock["High"]
    low = stock["Low"]
    volume = stock["Volume"]

    stock["LogReturn"] = np.log(close / close.shift(1))
    for name, window in (("SMA_5", 5), ("SMA_20", 20), ("SMA_50", 50), ("SMA_200", 200)):
        stock[name] = close.rolling(window).mean()
    stock["SMA_5_20_diff"] = (stock["SMA_5"] - stock["SMA_20"]) / stock["SMA_20"]
    stock["SMA_50_200_diff"] = (stock["SMA_50"] - stock["SMA_200"]) / stock["SMA_200"]
    stock["RSI"] = ta.momentum.RSIIndicator(close, window=14).rsi()

    macd = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
    stock["MACD"] = macd.macd()
    stock["MACD_Signal"] = macd.macd_signal()
    stock["MACD_Histogram"] = macd.macd_diff()

    bands = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    stock["BB_width"] = (
        bands.bollinger_hband() - bands.bollinger_lband()
    ) / bands.bollinger_mavg()
    stock["BB_pct"] = bands.bollinger_pband()
    stock["ATR_pct"] = (
        ta.volatility.AverageTrueRange(high, low, close, window=14)
        .average_true_range()
        .div(close)
    )
    obv = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
    stock["OBV_z"] = (obv - obv.rolling(20).mean()) / obv.rolling(20).std()
    return stock


def engineer_features(
    price_history: pd.DataFrame,
    vix_history: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Return trailing model features from raw OHLCV history.

    At least 200 chronological rows are required for every ticker because the
    feature contract contains a 200-session moving average. A single new row
    is therefore scored only after it is appended to an adequate history.
    """
    missing = sorted(REQUIRED_PRICE_COLUMNS.difference(price_history.columns))
    if missing:
        raise ValueError(f"Missing raw price columns: {missing}")

    frame = price_history.copy()
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    counts = frame.groupby("Ticker").size()
    short = counts[counts < MINIMUM_HISTORY_ROWS]
    if not short.empty:
        details = ", ".join(f"{ticker}={count}" for ticker, count in short.items())
        raise ValueError(
            f"At least {MINIMUM_HISTORY_ROWS} rows per ticker are required; received {details}."
        )

    featured = pd.concat(
        [_add_indicators(stock) for _, stock in frame.groupby("Ticker", sort=False)],
        ignore_index=True,
    )

    if vix_history is not None:
        vix = vix_history.copy()
        vix["Date"] = pd.to_datetime(vix["Date"])
        if "VIX_Close" not in vix.columns:
            if "Close" not in vix.columns:
                raise ValueError("VIX history must contain Close or VIX_Close.")
            vix = vix.rename(columns={"Close": "VIX_Close"})
        featured = featured.drop(columns=["VIX_Close"], errors="ignore").merge(
            vix[["Date", "VIX_Close"]], on="Date", how="left"
        )
    elif "VIX_Close" not in featured.columns:
        raise ValueError("VIX history is required when price history lacks VIX_Close.")

    featured["VIX_Close"] = featured.groupby("Ticker")["VIX_Close"].ffill()
    return featured.sort_values(["Ticker", "Date"]).reset_index(drop=True)


def latest_complete_features(
    price_history: pd.DataFrame,
    vix_history: pd.DataFrame | None = None,
    feature_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Return the most recent complete feature row for each ticker."""
    columns = feature_columns or FEATURE_COLUMNS
    featured = engineer_features(price_history, vix_history)
    complete = featured.dropna(subset=columns)
    latest = complete.groupby("Ticker", as_index=False, sort=False).tail(1)
    if latest.empty:
        raise ValueError("No complete feature rows were produced from the supplied history.")
    return latest[["Date", "Ticker", *columns]].reset_index(drop=True)
