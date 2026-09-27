# Stock Return Modeling Executive Summary

## Decision

Proceed with a controlled paper-trading trial. Do not allocate live capital at this stage.

The feedforward strategy produced positive net historical performance and remained profitable when transaction-cost assumptions increased. However, it underperformed SPY and the equal-weight stock universe over the final test period, and the evidence is not yet strong enough to support live deployment.

## Scope

The project evaluates short-horizon return forecasting across 50 US equities using market data from 2005 through 2025. Feedforward neural networks, an LSTM, linear regression, and transfer learning on chart images were tested with chronological data splits. The final comparison uses common ticker and date endpoints from December 8, 2022 through December 22, 2025.

The selected policy predicts each stock's next-trading-day log return. A positive prediction creates an equal-weight long position; a nonpositive prediction holds cash. The backtest charges 10 basis points whenever an asset-level position changes.

## Results

| Measure | Feedforward Strategy | SPY | Equal-Weight Universe |
|---|---:|---:|---:|
| Annualized return | 15.36% | 21.78% | 17.93% |
| Annualized volatility | 12.20% | 15.40% | 13.43% |
| Sharpe ratio | 1.17 | 1.28 | 1.23 |
| Maximum drawdown | -16.90% | -18.76% | -17.30% |
| Final value of $1 million | $1,540,296 | $1,814,476 | $1,646,661 |

The strategy generated $540,296 in simulated net profit, with 915 position changes, 2.40% average daily turnover, and a 52.59% active-position win rate. Its Sharpe ratio declined from 1.22 before costs to 1.17 at 10 basis points and 1.12 at 20 basis points.

The feedforward network slightly improved MSE over linear regression and produced a substantially higher net Sharpe with lower turnover. The larger LSTM did not improve MSE or net Sharpe. The image models achieved test AUROC values of 0.508 and 0.512, which is too close to random ranking to justify further promotion.

## Interpretation

The result supports continued evaluation, not a claim of market-beating performance. The model reduced volatility and drawdown relative to SPY, but it also produced lower return and lower risk-adjusted performance. Its strongest evidence is operational: the pipeline is reproducible, costs are included, the signal remains positive under higher cost assumptions, and inference can fail closed to cash when inputs or artifacts are invalid.

## Risks

The stock universe may contain survivorship bias. Only one training seed is recorded, and overlapping market observations reduce the reliability of naive statistical error estimates. The backtest does not model market impact, changing bid-ask spreads, taxes, latency, capacity constraints, rejected orders, or live-data failures. Performance has not yet been formally measured across predefined market regimes.

## Next Decision Gate

Run a monitored paper-trading trial for at least 60 trading days. Continue only if data-quality checks pass, rolling net Sharpe remains positive, drawdown stays within the -25% limit, turnover remains close to the tested range, and no material feature or prediction drift appears. A live-capital decision should also require repeated-seed training, dependence-aware confidence intervals, and a new locked temporal holdout.
