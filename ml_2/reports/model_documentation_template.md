# Model Documentation

## Purpose

Describe the prediction horizon, target, eligible assets, and intended decision.

## Data

Record the source, date range, temporal split boundaries, features, target construction, missing-value handling, and known biases.

## Methodology

Document the baseline, neural-network architecture, loss, optimizer, early stopping, random seed, and walk-forward procedure.

## Evaluation

Report MSE, MAE, directional accuracy, net Sharpe ratio, maximum drawdown, and transaction-cost assumption. Separate validation results from the untouched test result.

## Limitations

Cover survivorship bias, non-stationarity, market impact, slippage, corporate actions, and the fact that research performance does not guarantee live performance.

## Monitoring

Define drift, data-quality, latency, turnover, drawdown, and performance thresholds that trigger investigation or retraining.

## Reproduction

Record the code revision, package versions, data snapshot, random seed, saved scaler, feature list, and model checkpoint.
