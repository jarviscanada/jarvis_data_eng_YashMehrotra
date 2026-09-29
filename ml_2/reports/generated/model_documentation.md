# Feedforward Return Model Documentation

## Business purpose

Rank the next-trading-day return sign for a 50-ticker US equity universe and support an equal-weight long-or-cash paper-trading policy. The model is intended for paper-trading evaluation and is not approved for live orders.

## Inputs and outputs

- Input: the 12 engineered and training-scaled features listed in `models/feature_cols.joblib`.
- Output: predicted next-day log return.
- Decision: long when the prediction is positive; otherwise hold cash.
- Batch interface: `src.inference.ReturnPredictionService`.
- Raw-history interface: `ReturnPredictionService.score_raw_history`, which recreates trailing features, applies the saved training scaler, and scores the latest complete row.

The service rejects missing columns and non-finite feature values. A new market row must be appended to at least 200 sessions of OHLCV history because the feature contract includes a 200-session moving average. The raw-history interface uses the same formulas as Notebook 02 and the fitted training scaler.

## Training and validation

- Chronological training period ends before the validation period; the test period starts on 2022-12-08.
- Architecture: fully connected 128-64-32 network with batch normalization, ReLU, and 0.3 dropout.
- Optimizer: Adam with MSE loss, 100-epoch cap, and validation early stopping.
- Random seed: 42.
- Primary checkpoint: `models/feedforward_nn_step3.pt`.

The feedforward model was registered as primary before final test evaluation. The LSTM and linear regression are challengers evaluated on identical endpoints.

## Untouched-test result

- Net annualized return: 15.36%.
- Net annualized volatility: 12.20%.
- Net Sharpe ratio: 1.17.
- Maximum drawdown: -16.90%.
- Directional accuracy: 52.08%.
- Assumed cost: 10 basis points per position change.
- Hypothetical $1 million ending value: $1,540,296.

SPY produced a 1.28 Sharpe ratio and 21.78% annualized return over the same dates, so the strategy does not beat the benchmark. The appropriate recommendation is controlled paper trading for operational validation, not capital allocation.

## Controls and monitoring

- Fail closed to cash on schema, missing-data, non-finite-value, stale-date, or model-load errors.
- Monitor 20-day and 60-day directional accuracy, net return, turnover, and drawdown.
- Investigate material feature drift monthly.
- Alert when 60-day Sharpe is below zero, drawdown breaches -10%, or daily turnover exceeds twice the test average.
- Retrain through the same temporal pipeline and approve replacements on validation data before a final holdout test.

## Limitations

The dataset may contain survivorship bias. The backtest omits market impact, taxes, latency, capacity constraints, and live-data failures. Historical performance is regime-dependent. The five-day chart-image pilot is a separate research challenger and is not part of this deployment package.
