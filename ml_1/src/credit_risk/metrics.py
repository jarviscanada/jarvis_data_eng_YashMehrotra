"""Credit-risk model evaluation helpers."""

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


def optimal_f1_threshold(y_true, probabilities) -> float:
    """Return the probability threshold that maximizes F1."""
    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)
    if len(thresholds) == 0:
        return 0.5
    numerator = 2 * precision[:-1] * recall[:-1]
    denominator = precision[:-1] + recall[:-1]
    f1_values = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator),
        where=denominator != 0,
    )
    return float(thresholds[int(np.nanargmax(f1_values))])


def evaluate_probabilities(y_true, probabilities, threshold=None) -> dict[str, float]:
    """Calculate discrimination, calibration, and classification metrics."""
    if threshold is None:
        threshold = optimal_f1_threshold(y_true, probabilities)
    predictions = (probabilities >= threshold).astype("int8")
    fpr, tpr, _ = roc_curve(y_true, probabilities)
    auroc = roc_auc_score(y_true, probabilities)
    return {
        "AUROC": float(auroc),
        "Gini": float(2 * auroc - 1),
        "KS": float(np.max(tpr - fpr)),
        "AUPRC": float(average_precision_score(y_true, probabilities)),
        "F1": float(f1_score(y_true, predictions)),
        "Brier": float(brier_score_loss(y_true, probabilities)),
        "threshold": float(threshold),
    }
