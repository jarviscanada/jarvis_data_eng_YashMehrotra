"""Load the approved feedforward artifact and produce auditable predictions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch

from .features import latest_complete_features
from .modeling import FeedForwardNN


@dataclass
class ReturnPredictionService:
    """Small inference boundary for batch scoring already-engineered features."""

    model: FeedForwardNN
    feature_columns: list[str]
    scaler: object
    device: torch.device

    @classmethod
    def load(cls, model_dir: str | Path, device: str = "cpu") -> "ReturnPredictionService":
        model_dir = Path(model_dir)
        torch_device = torch.device(device)
        feature_columns = list(joblib.load(model_dir / "feature_cols.joblib"))
        scaler = joblib.load(model_dir / "feature_scaler.joblib")
        checkpoint = torch.load(
            model_dir / "feedforward_nn_step3.pt",
            map_location=torch_device,
            weights_only=False,
        )
        if checkpoint["input_size"] != len(feature_columns):
            raise ValueError("Checkpoint input size does not match the feature contract.")
        model = FeedForwardNN(
            input_size=checkpoint["input_size"],
            hidden_sizes=tuple(checkpoint["hidden_sizes"]),
            dropout=checkpoint["dropout"],
        ).to(torch_device)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        return cls(
            model=model,
            feature_columns=feature_columns,
            scaler=scaler,
            device=torch_device,
        )

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        missing = sorted(set(self.feature_columns).difference(features.columns))
        if missing:
            raise ValueError(f"Missing model features: {missing}")
        matrix = features[self.feature_columns].to_numpy(dtype=np.float32)
        if not np.isfinite(matrix).all():
            raise ValueError("Model features contain missing or non-finite values.")
        with torch.no_grad():
            predictions = self.model(torch.as_tensor(matrix, device=self.device)).squeeze(1)
        return predictions.cpu().numpy()

    def score(self, rows: pd.DataFrame) -> pd.DataFrame:
        """Score rows whose model features are already training-scaled."""

        scored = rows[[column for column in ("Date", "Ticker") if column in rows]].copy()
        scored["prediction"] = self.predict(rows)
        scored["position"] = (scored["prediction"] > 0).astype(int)
        return scored

    def score_raw_history(
        self,
        price_history: pd.DataFrame,
        vix_history: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        """Engineer, scale, and score the latest raw OHLCV row per ticker.

        The new observation must be supplied with at least 200 sessions of
        history so every rolling feature can be reproduced exactly.
        """
        latest = latest_complete_features(
            price_history,
            vix_history=vix_history,
            feature_columns=self.feature_columns,
        )
        scaled = latest.copy()
        scaled[self.feature_columns] = self.scaler.transform(
            latest[self.feature_columns]
        )
        return self.score(scaled)
