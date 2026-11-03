"""Train a direction classifier plus a return head on already training-scaled CSVs."""
import argparse
import json
import os
import random
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

FEATURE_COLS = ['LogReturn', 'SMA_5_20_diff', 'SMA_50_200_diff', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'BB_width', 'BB_pct', 'ATR_pct', 'OBV_z', 'VIX_Close']
TARGET_COL = "target_next_day_logreturn"

class FeedForwardNN(nn.Module):
    def __init__(self, input_dim=12):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(input_dim, 32), nn.ReLU(),
                                 nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 2))
    def forward(self, x):
        return self.net(x)

def load_frame(path):
    frame = pd.read_csv(path)
    values = frame[FEATURE_COLS + [TARGET_COL]].to_numpy(dtype=np.float32)
    if not np.isfinite(values).all():
        raise ValueError(f"Non-finite features or targets in {path}")
    return frame, torch.from_numpy(values[:, :-1].copy()), torch.from_numpy(values[:, -1].copy())

def choose_threshold(probabilities, labels):
    # Evaluate decisions using both classes, rather than raw accuracy in a rising market.
    best = None
    for threshold in np.linspace(0.30, 0.70, 81):
        decisions = probabilities > threshold
        tpr = decisions[labels].mean()
        tnr = (~decisions[~labels]).mean()
        balanced = float((tpr + tnr) / 2)
        candidate = (balanced, -abs(threshold - 0.5), float(threshold))
        if best is None or candidate > best:
            best = candidate
    return best[2], best[0]

def train(args):
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_df, x, returns = load_frame(Path(args.train_dir) / "train.csv")
    val_df, vx, vr = load_frame(Path(args.validation_dir) / "val.csv")
    if pd.to_datetime(train_df.Date).max() >= pd.to_datetime(val_df.Date).min():
        raise ValueError("Training and validation dates overlap")
    labels = (returns > 0).float()
    vl = (vr.numpy() > 0)
    if len(np.unique(labels.numpy())) != 2 or len(np.unique(vl)) != 2:
        raise ValueError("Both return directions are required in training and validation")
    mean, scale = returns.mean().item(), returns.std().item()
    if scale <= 0:
        raise ValueError("Target variance must be positive")
    # Class weighting makes the direction task sensitive to down days as well as up days.
    positives = labels.sum().item()
    pos_weight = torch.tensor([(len(labels) - positives) / positives], device=device)
    bce = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    mse = nn.MSELoss()
    winner = None
    metrics = []
    for seed in args.seeds:
        random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
        if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
        model = FeedForwardNN().to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate,
                                      weight_decay=args.weight_decay)
        loader = DataLoader(TensorDataset(x, labels, (returns-mean)/scale),
                            batch_size=args.batch_size, shuffle=True)
        best_loss, stale, state = float("inf"), 0, None
        for epoch in range(args.epochs):
            model.train()
            for bx, by, br in loader:
                output = model(bx.to(device))
                loss = bce(output[:, 0], by.to(device)) + 0.1*mse(output[:, 1], br.to(device))
                optimizer.zero_grad(); loss.backward(); optimizer.step()
            model.eval()
            with torch.no_grad():
                output = model(vx.to(device))
                loss = (bce(output[:, 0], torch.tensor(vl, dtype=torch.float32, device=device))
                        + 0.1*mse(output[:, 1], ((vr-mean)/scale).to(device))).item()
            print(f"seed={seed} epoch={epoch+1} validation_loss={loss:.6f}", flush=True)
            if loss < best_loss - 1e-6:
                best_loss, stale = loss, 0
                state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            else:
                stale += 1
            if stale >= args.patience: break
        model.load_state_dict(state); model.eval()
        with torch.no_grad():
            output = model(vx.to(device)).cpu()
        probabilities = output[:, 0].sigmoid().numpy()
        threshold, balanced = choose_threshold(probabilities, vl)
        decisions = probabilities > threshold
        result = dict(seed=seed, validation_balanced_accuracy=balanced,
                      threshold=threshold, validation_long=int(decisions.sum()),
                      validation_cash=int((~decisions).sum()),
                      probability_std=float(probabilities.std()), validation_loss=best_loss)
        print(json.dumps(result), flush=True)
        metrics.append(result)
        if winner is None or balanced > winner[0]:
            winner = (balanced, state, result)
    output_dir = Path(args.model_dir); output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "validation_metrics.json").write_text(json.dumps(metrics, indent=2))
    balanced, state, result = winner
    # Fail the job instead of deploying a constant signal or an ineffective classifier.
    if result['validation_long'] == 0 or result['validation_cash'] == 0 or balanced < args.min_balanced_accuracy:
        raise RuntimeError("Validation deployment gate failed; do not deploy this run. See validation_metrics.json and training logs.")
    checkpoint = dict(model_state_dict=state, feature_columns=FEATURE_COLS,
                      threshold=result['threshold'], return_mean=mean, return_scale=scale,
                      format_version=2, validation=result)
    torch.save(checkpoint, output_dir / "feedforward_nn.pt")
    print("Saved validated model", json.dumps(result), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-dir', default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--validation-dir', default=os.environ.get('SM_CHANNEL_VAL'))
    parser.add_argument('--model-dir', default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--batch-size', type=int, default=512)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--patience', type=int, default=10)
    parser.add_argument('--learning-rate', type=float, default=0.001)
    parser.add_argument('--weight-decay', type=float, default=0.000001)
    parser.add_argument('--seeds', type=int, nargs='+', default=[42, 43, 44])
    parser.add_argument('--min-balanced-accuracy', type=float, default=0.505)
    train(parser.parse_args())
