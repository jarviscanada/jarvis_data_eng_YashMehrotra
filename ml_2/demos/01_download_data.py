"""
Demo 01: Download S&P 500 Stock Data
=====================================
Module 2 - Introduction to Deep Learning
ML Engineer Training Curriculum

This script downloads historical OHLCV data for 50 S&P 500 stocks
plus supplementary market data (VIX, Treasury yields).

Usage:
    python demos/01_download_data.py

Output:
    data/sp500_stocks.csv      - Daily OHLCV for 50 stocks
    data/vix.csv               - CBOE Volatility Index
    data/treasury_10y.csv      - 10-Year Treasury Yield
"""

import os
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

# ── Configuration ──
OUTPUT_DIR = "data"
START_DATE = "2005-01-01"
END_DATE = "2025-12-31"

# 50 S&P 500 stocks across sectors for diversification
TICKERS = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "AVGO", "CRM",
    # Financials
    "JPM", "BAC", "GS", "MS", "WFC", "BLK", "C", "AXP",
    # Healthcare
    "UNH", "JNJ", "PFE", "ABBV", "MRK", "LLY",
    # Consumer
    "WMT", "PG", "KO", "PEP", "COST", "MCD", "NKE",
    # Energy
    "XOM", "CVX", "COP", "SLB",
    # Industrials
    "CAT", "BA", "HON", "UPS", "GE",
    # Communication
    "DIS", "NFLX", "CMCSA", "VZ",
    # Materials & Utilities
    "LIN", "APD", "NEE", "DUK",
    # Real Estate & Other
    "AMT", "PLD", "SPY", "QQQ",  # Include SPY and QQQ as benchmarks
]

# Supplementary market data
MARKET_TICKERS = {
    "vix": "^VIX",
    "treasury_10y": "^TNX",
}


def flatten_columns(df):
    """Flatten multi-level columns returned by newer yfinance versions."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def download_stock_data(tickers, start, end):
    """Download OHLCV data for a list of tickers."""
    print(f"Downloading data for {len(tickers)} tickers from {start} to {end}...")

    all_data = []
    failed = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            if df.empty:
                failed.append(ticker)
                continue
            df = flatten_columns(df)
            df["Ticker"] = ticker
            df.index.name = "Date"
            all_data.append(df.reset_index())
            print(f"  ✓ {ticker}: {len(df)} rows ({df.index[0].date()} to {df.index[-1].date()})")
        except Exception as e:
            failed.append(ticker)
            print(f"  ✗ {ticker}: {e}")

    if failed:
        print(f"\nFailed tickers: {failed}")

    combined = pd.concat(all_data, ignore_index=True)
    return combined


def download_market_data(ticker_dict, start, end):
    """Download supplementary market data (VIX, Treasury yields)."""
    results = {}
    for name, ticker in ticker_dict.items():
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            if not df.empty:
                df = flatten_columns(df)
                df.index.name = "Date"
                results[name] = df.reset_index()
                print(f"  ✓ {name} ({ticker}): {len(df)} rows")
        except Exception as e:
            print(f"  ✗ {name} ({ticker}): {e}")
    return results


def compute_basic_stats(df):
    """Compute summary statistics per stock."""
    # Determine which close column is available
    close_col = "Adj Close" if "Adj Close" in df.columns else "Close"

    stats = []
    for ticker in df["Ticker"].unique():
        stock = df[df["Ticker"] == ticker].sort_values("Date")
        prices = stock[close_col].dropna().values.astype(float)

        # Need at least 2 prices to compute returns
        if len(prices) < 2:
            print(f"  ⚠ {ticker}: not enough data ({len(prices)} prices), skipping")
            continue

        # Daily log returns
        log_returns = np.log(prices[1:] / prices[:-1])
        # Remove any inf or nan
        log_returns = log_returns[np.isfinite(log_returns)]

        if len(log_returns) == 0:
            print(f"  ⚠ {ticker}: no valid returns, skipping")
            continue

        # Annualized metrics (252 trading days)
        ann_return = float(np.mean(log_returns) * 252)
        ann_vol = float(np.std(log_returns, ddof=1) * (252 ** 0.5))
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0

        # Max drawdown
        cumulative = np.cumprod(1 + log_returns)
        rolling_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - rolling_max) / rolling_max
        max_dd = float(np.min(drawdown)) if len(drawdown) > 0 else 0.0

        stats.append({
            "Ticker": ticker,
            "Annualized Return": round(ann_return, 4),
            "Annualized Volatility": round(ann_vol, 4),
            "Sharpe Ratio": round(sharpe, 4),
            "Max Drawdown": round(max_dd, 4),
            "Total Days": len(stock),
        })

    return pd.DataFrame(stats).sort_values("Sharpe Ratio", ascending=False)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Download stock data
    print("=" * 60)
    print("STEP 1: Downloading S&P 500 Stock Data")
    print("=" * 60)
    stocks_df = download_stock_data(TICKERS, START_DATE, END_DATE)
    stocks_path = os.path.join(OUTPUT_DIR, "sp500_stocks.csv")
    stocks_df.to_csv(stocks_path, index=False)
    print(f"\nSaved {len(stocks_df)} rows to {stocks_path}")
    print(f"Shape: {stocks_df.shape}")
    print(f"Tickers: {stocks_df['Ticker'].nunique()}")
    print(f"Date range: {stocks_df['Date'].min()} to {stocks_df['Date'].max()}")

    # 2. Download market data
    print("\n" + "=" * 60)
    print("STEP 2: Downloading Market Data (VIX, Treasury)")
    print("=" * 60)
    market_data = download_market_data(MARKET_TICKERS, START_DATE, END_DATE)
    for name, df in market_data.items():
        path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"Saved {name} to {path}")

    # 3. Summary statistics
    print("\n" + "=" * 60)
    print("STEP 3: Summary Statistics")
    print("=" * 60)
    stats = compute_basic_stats(stocks_df)
    print("\nTop 10 Stocks by Sharpe Ratio:")
    print(stats.head(10).to_string(index=False))
    print("\nBottom 5 Stocks by Sharpe Ratio:")
    print(stats.tail(5).to_string(index=False))

    stats_path = os.path.join(OUTPUT_DIR, "stock_summary_stats.csv")
    stats.to_csv(stats_path, index=False)
    print(f"\nSaved summary stats to {stats_path}")

    print("\n" + "=" * 60)
    print("DATA DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"\nFiles in {OUTPUT_DIR}/:")
    for f in os.listdir(OUTPUT_DIR):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"  {f} ({size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()