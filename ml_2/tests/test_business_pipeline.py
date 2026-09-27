from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from src.backtesting import execution_metrics, performance_metrics, run_long_cash_backtest
from src.inference import ReturnPredictionService


ROOT = Path(__file__).resolve().parents[1]


class BacktestTests(unittest.TestCase):
    def test_cost_is_charged_when_position_changes(self):
        rows = pd.DataFrame(
            {
                "Date": pd.to_datetime(["2026-01-02", "2026-01-05", "2026-01-06"]),
                "Ticker": ["A", "A", "A"],
                "prediction": [0.1, -0.1, 0.1],
                "actual_return": [0.01, 0.02, -0.01],
            }
        )
        assets, daily = run_long_cash_backtest(rows, transaction_cost_bps=10)
        np.testing.assert_allclose(assets["cost"], [0.001, 0.001, 0.001])
        self.assertEqual(execution_metrics(assets)["trades"], 3)
        self.assertEqual(performance_metrics(daily)["trading_days"], 3)

    def test_missing_contract_column_is_rejected(self):
        rows = pd.DataFrame({"Date": ["2026-01-02"]})
        with self.assertRaisesRegex(ValueError, "Missing columns"):
            run_long_cash_backtest(rows)


class InferenceTests(unittest.TestCase):
    def test_saved_primary_model_loads_and_scores(self):
        service = ReturnPredictionService.load(ROOT / "models")
        test = pd.read_csv(ROOT / "data" / "processed" / "test.csv", nrows=3)
        scored = service.score(test)
        self.assertEqual(list(scored.columns), ["Date", "Ticker", "prediction", "position"])
        self.assertTrue(np.isfinite(scored["prediction"]).all())

    def test_missing_feature_is_rejected(self):
        service = ReturnPredictionService.load(ROOT / "models")
        with self.assertRaisesRegex(ValueError, "Missing model features"):
            service.predict(pd.DataFrame({"not_a_feature": [1.0]}))

    def test_raw_history_requires_rolling_context(self):
        service = ReturnPredictionService.load(ROOT / "models")
        one_row = pd.DataFrame(
            {
                "Date": ["2026-01-02"],
                "Ticker": ["AAPL"],
                "Close": [100.0],
                "High": [101.0],
                "Low": [99.0],
                "Volume": [1_000_000],
                "VIX_Close": [15.0],
            }
        )
        with self.assertRaisesRegex(ValueError, "At least 200 rows"):
            service.score_raw_history(one_row)


if __name__ == "__main__":
    unittest.main()
