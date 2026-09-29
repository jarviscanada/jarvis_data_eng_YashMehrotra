"""Run a small, deterministic long-or-cash backtesting demonstration."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.backtesting import performance_metrics, run_long_cash_backtest


def main() -> None:
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2022-01-03", periods=500)
    actual = rng.normal(0.0003, 0.012, len(dates))
    signal = 0.15 * actual + rng.normal(0, 0.015, len(dates))

    predictions = pd.DataFrame(
        {
            "Date": dates,
            "Ticker": "DEMO",
            "prediction": signal,
            "actual_return": actual,
        }
    )
    _, daily = run_long_cash_backtest(predictions, transaction_cost_bps=10)
    metrics = performance_metrics(daily)

    print("Long-or-cash backtest, net of 10 bps per position change")
    for name, value in metrics.items():
        print(f"{name:24s} {value:,.4f}" if isinstance(value, float) else f"{name:24s} {value}")


if __name__ == "__main__":
    main()
