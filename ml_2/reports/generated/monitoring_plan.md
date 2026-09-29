# Monitoring Plan

- Run daily input checks for missing tickers, non-finite features, schema changes, and stale dates.
- Track feature drift monthly against the training distribution and investigate material shifts.
- Track 20-day and 60-day directional accuracy, net return, turnover, and drawdown after labels mature.
- Alert when 60-day Sharpe is below 0, drawdown breaches -10%, or daily turnover exceeds twice the test average.
- Retrain only through the documented temporal pipeline; approve a replacement on validation data before one final test.
- Roll back to cash if data validation fails or the model artifact cannot be loaded.
