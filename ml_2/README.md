# Stock Return Deep Learning and Backtesting

## Overview

This project tests whether deep learning can forecast short-horizon US equity returns and produce a useful trading signal after transaction costs. It covers 50 US equities from 2005 through 2025 and compares feedforward, LSTM, linear, and chart-image approaches under chronological validation.

The selected feedforward model produced positive historical performance, but it did not beat SPY or an equal-weight stock benchmark during the final test period. The project therefore recommends controlled paper trading, not live deployment.

## Key Results

The final test period runs from December 8, 2022 through December 22, 2025. The strategy holds each stock when its predicted next-day return is positive and otherwise holds cash. Results include a 10-basis-point cost whenever an asset-level position changes.

| Result | Feedforward Strategy | SPY | Equal-Weight Universe |
|---|---:|---:|---:|
| Annualized return | 15.36% | 21.78% | 17.93% |
| Sharpe ratio | 1.17 | 1.28 | 1.23 |
| Maximum drawdown | -16.90% | -18.76% | -17.30% |
| Final value of $1 million | $1.54M | $1.81M | $1.65M |

The feedforward model achieved 52.08% directional accuracy and lower turnover than the linear baseline. The LSTM reached 52.20% directional accuracy but had worse MSE and net Sharpe. The chart-image models produced AUROC values near 0.51, which did not support promotion.

## Workflow

Run the notebooks in order:

1. `01_eda.ipynb` — audits the market data and analyzes returns, volatility, and VIX.
2. `02_preprocessing.ipynb` — creates trailing features, future-return targets, chronological splits, and the training scaler.
3. `03_feedforward_nn.ipynb` — trains feedforward networks and compares them with linear regression.
4. `04_sequence_models.ipynb` — evaluates an LSTM, walk-forward validation, and sequence-length choices.
5. `05_transfer_learning.ipynb` — tests ResNet-18 and frozen image features on chart images.
6. `06_backtesting.ipynb` — compares final models, applies costs, evaluates benchmarks, and writes the reporting package.

Reusable feature engineering, model definitions, inference, and portfolio calculations live in `src/`. Generated reports and evaluation files are written to `reports/generated/`.

## Quick Start

Create a Python 3.11 environment from the `ml_2` directory:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS or Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter notebook
```

PyTorch installation depends on the operating system and CUDA version. Install the appropriate PyTorch build separately if needed.

Run the automated tests with:

```bash
python -m unittest discover -s tests -v
```

## Modeling Approach

The tabular models use 12 trailing features based on returns, moving-average spreads, RSI, MACD, Bollinger Bands, ATR, volume, and VIX. The main target is next-trading-day log return. Data is divided by unique dates into non-overlapping training, validation, and test periods.

The primary model is a feedforward network with hidden layers of 128, 64, and 32 units. Each block uses linear transformation, batch normalization, ReLU, and dropout. The model is trained with Adam, mean squared error, weight decay, and validation-based early stopping.

The LSTM uses 60-day sequences and two recurrent layers. The image pilot uses 30-session chart images and a five-day directional target, so its results are reported separately from the next-day model comparison.

## Leakage and Reproducibility Controls

- Features are calculated independently within each ticker using trailing data.
- Dataset splits follow time order and do not share boundary dates.
- Forward targets that cross split boundaries are removed.
- The scaler is fitted only on training data.
- Walk-forward folds refit preprocessing using only prior observations.
- Final model comparisons use identical ticker and date endpoints.
- The primary model is fixed before the final test comparison.
- Backtests include transaction costs and benchmark comparisons.
- Saved feature order, scaler, checkpoint, and model manifest support repeatable inference.

## Project Structure

```text
ml_2/
├── notebooks/          # Six analytical notebooks
├── src/                # Features, models, inference, and backtesting
├── tests/              # Business-pipeline tests
├── data/               # Raw and processed market data
├── models/             # Checkpoints, scaler, feature list, and manifest
├── reports/generated/  # Results and summary
├── demos/              # Standalone workflow examples
├── requirements.txt
└── README.md
```

Important outputs include:

- `reports/generated/executive_summary.md`
- `reports/generated/model_documentation.md`
- `reports/generated/model_comparison.csv`
- `reports/generated/portfolio_comparison.csv`
- `reports/generated/cost_sensitivity.csv`

## Decision and Limitations

The model meets the stated paper-trading criteria: positive net Sharpe, maximum drawdown better than -25%, and positive Sharpe when assumed costs increase to 20 basis points. It is not ready for live trading.

The main limitations are a single recorded training seed, possible survivorship bias in the 50-stock universe, correlated observations, limited regime analysis, and an execution simulation that omits market impact, changing spreads, taxes, latency, capacity limits, and live-data failures. Historical performance does not establish future profitability.

Before any live-capital decision, the project should complete repeated-seed evaluation, block-bootstrap uncertainty estimates, point-in-time universe testing, formal regime analysis, and a monitored paper-trading trial.
