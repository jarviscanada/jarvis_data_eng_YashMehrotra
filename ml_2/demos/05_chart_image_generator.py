"""Generate clean candlestick images for transfer-learning experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw


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

    opens = window["Open"].to_numpy(float)
    highs = window["High"].to_numpy(float)
    lows = window["Low"].to_numpy(float)
    closes = window["Close"].to_numpy(float)
    price_low = lows.min()
    price_range = max(highs.max() - price_low, 1e-6)

    image = Image.new("RGB", (image_size, image_size), "white")
    draw = ImageDraw.Draw(image)
    margin = 4
    x_step = (image_size - 2 * margin) / len(window)

    def y_coordinate(price: float) -> int:
        normalized = (price - price_low) / price_range
        return round(image_size - margin - normalized * (image_size - 2 * margin))

    for index in range(len(window)):
        color = "#15803d" if closes[index] >= opens[index] else "#b91c1c"
        x = round(margin + (index + 0.5) * x_step)
        draw.line((x, y_coordinate(highs[index]), x, y_coordinate(lows[index])), fill=color, width=1)
        top = min(y_coordinate(opens[index]), y_coordinate(closes[index]))
        bottom = max(y_coordinate(opens[index]), y_coordinate(closes[index]), top + 1)
        half_width = max(1, round(x_step * 0.3))
        draw.rectangle((x - half_width, top, x + half_width, bottom), fill=color, outline=color)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG", optimize=False)


def generate_images(
    data_path: Path,
    output_dir: Path,
    *,
    tickers: list[str],
    window_size: int = 30,
    horizon: int = 5,
    stride: int = 1,
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
    parser.add_argument("--stride", type=int, default=1)
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
