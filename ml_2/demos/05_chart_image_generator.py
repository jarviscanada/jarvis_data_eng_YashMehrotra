"""Generate clean candlestick images for transfer-learning experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd


def render_candlestick_window(
    window: pd.DataFrame,
    output_path: Path,
    *,
    image_size: int = 224,
) -> None:
    """Render an OHLC window without text, axes, or time-reversing transforms."""

    required = {"Open", "High", "Low", "Close"}
    missing = required.difference(window.columns)
    if missing:
        raise ValueError(f"Missing OHLC columns: {sorted(missing)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(image_size / 100, image_size / 100), dpi=100)
    axis = figure.add_axes([0, 0, 1, 1])

    opens = window["Open"].to_numpy(float)
    highs = window["High"].to_numpy(float)
    lows = window["Low"].to_numpy(float)
    closes = window["Close"].to_numpy(float)
    x = np.arange(len(window))
    price_range = max(highs.max() - lows.min(), 1e-6)

    for index in range(len(window)):
        color = "#15803d" if closes[index] >= opens[index] else "#b91c1c"
        axis.vlines(x[index], lows[index], highs[index], color=color, linewidth=1)
        body_low = min(opens[index], closes[index])
        body_height = max(abs(closes[index] - opens[index]), price_range * 0.002)
        axis.add_patch(
            Rectangle(
                (x[index] - 0.3, body_low),
                0.6,
                body_height,
                facecolor=color,
                edgecolor=color,
                linewidth=0.7,
            )
        )

    axis.set_xlim(-1, len(window))
    axis.set_ylim(lows.min() - 0.05 * price_range, highs.max() + 0.05 * price_range)
    axis.axis("off")
    figure.savefig(output_path, dpi=100, pad_inches=0)
    plt.close(figure)


def generate_images(
    data_path: Path,
    output_dir: Path,
    *,
    tickers: list[str],
    window_size: int = 30,
    horizon: int = 5,
    stride: int = 20,
) -> pd.DataFrame:
    """Generate images and return their dates, labels, and future returns."""

    market = pd.read_csv(data_path, parse_dates=["Date"])
    market = market.sort_values(["Ticker", "Date"])
    records: list[dict[str, object]] = []

    for ticker in tickers:
        stock = market[market["Ticker"] == ticker].reset_index(drop=True)
        for end in range(window_size - 1, len(stock) - horizon, stride):
            prediction_date = stock.loc[end, "Date"]
            future_return = np.log(stock.loc[end + horizon, "Close"] / stock.loc[end, "Close"])
            image_path = output_dir / ticker / f"{prediction_date:%Y%m%d}.png"
            if not image_path.exists():
                render_candlestick_window(
                    stock.iloc[end - window_size + 1 : end + 1],
                    image_path,
                )
            records.append(
                {
                    "Ticker": ticker,
                    "Date": prediction_date,
                    "image_path": str(image_path),
                    "next_5d_log_return": future_return,
                    "label": int(future_return > 0),
                }
            )

    return pd.DataFrame(records).sort_values(["Date", "Ticker"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/sp500_stocks.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/chart_images_demo"))
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "MSFT"])
    parser.add_argument("--stride", type=int, default=20)
    args = parser.parse_args()

    labels = generate_images(
        args.data,
        args.output,
        tickers=args.tickers,
        stride=args.stride,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    labels.to_csv(args.output / "labels.csv", index=False)
    print(f"Generated {len(labels):,} images in {args.output}")


if __name__ == "__main__":
    main()
