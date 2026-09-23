# Module 2 Introduction to Deep Learning

This module builds a reproducible stock-return modeling workflow with financial EDA, leakage-safe feature engineering, feedforward networks, LSTMs, transfer learning, and a transaction-cost-aware backtest. The notebooks favor clear code and honest baselines over model complexity.

## Project layout

- `data/`: raw and processed market data
- `demos/`: small standalone examples, including chart rendering and backtesting
- `notebooks/`: the guided capstone in execution order
- `src/`: reusable project code
- `models/`: fitted scalers, feature lists, and model checkpoints
- `reports/`: report templates and generated backtest artifacts

## Setup

Create a Python 3.11 environment, then install the module dependencies:

```bash
python -m pip install -r ml_2/requirements.txt
```

PyTorch installation can vary by operating system and GPU. If the command above does not install the desired build, install PyTorch first using the command recommended for your platform, then install the remaining requirements.

## Notebook order

Run notebooks from the `ml_2/notebooks` directory or from the repository root. Paths are resolved in either location.

1. `01_eda.ipynb` explores returns, volatility, correlations, VIX, and missing sessions.
2. `02_preprocessing.ipynb` creates per-ticker indicators and targets, performs non-overlapping temporal splits, and fits the scaler only on training data.
3. `03_feedforward_nn.ipynb` compares neural-network architectures with linear regression.
4. `04_sequence_models.ipynb` trains an LSTM, runs walk-forward validation, and studies sequence length and temporal importance.
5. `05_transfer_learning.ipynb` creates chart images, compares transfer-learning approaches, and visualizes Grad-CAM.
6. `06_backtesting.ipynb` runs the final net-of-costs backtest and writes business-facing outputs.

Notebooks 03, 04, and 05 expose `FAST_MODE = True`. Keep it enabled for a classroom run. In notebook 03 it shortens the extra architecture comparisons while preserving the primary model's full early-stopping budget. In notebook 04 it uses five representative tickers, and in notebook 05 it uses a 20-session image stride and two epochs. Set it to `False` for the full experiments.

## Reproducibility rules

- All random seeds are set to 42.
- Returns and indicators are computed within each ticker.
- Splits are chronological and do not share boundary dates.
- The scaler is fitted only on training rows.
- Forward-label samples that cross a split boundary are purged.
- Test data is evaluated only after model selection.
- Trading results include 10 basis points per position change.

## Standalone demos

```bash
python ml_2/demos/01_download_data.py
python ml_2/demos/05_chart_image_generator.py --tickers AAPL MSFT
python ml_2/demos/08_backtesting.py
```

The chart demo uses a stride of 20 by default so it finishes quickly. Use `--stride 1` to generate every eligible daily window.

## Deliverables

Notebook 06 saves generated metrics, predictions, monthly returns, the equity curve, and a draft executive summary under `reports/generated/`. Review the result against the templates in `reports/` before presenting it. A positive research backtest is not evidence that a live strategy will remain profitable.
