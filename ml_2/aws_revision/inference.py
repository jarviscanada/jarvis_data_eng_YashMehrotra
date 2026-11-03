"""Version 2 serving contract; inputs must already use the training scaler."""
import json
import os
import torch
from torch import nn

class FeedForwardNN(nn.Module):
    def __init__(self, input_dim=12):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(input_dim, 32), nn.ReLU(),
                                 nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 2))
    def forward(self, x): return self.net(x)

def model_fn(model_dir):
    checkpoint = torch.load(os.path.join(model_dir, 'feedforward_nn.pt'),
                            map_location='cpu', weights_only=True)
    if checkpoint.get('format_version') != 2:
        raise ValueError('This inference script requires a newly trained version 2 checkpoint')
    model = FeedForwardNN(len(checkpoint['feature_columns']))
    model.load_state_dict(checkpoint['model_state_dict']); model.eval()
    return model, checkpoint

def input_fn(request_body, content_type):
    if content_type.split(';')[0] != 'application/json':
        raise ValueError('Expected application/json')
    data = json.loads(request_body)
    x = torch.tensor(data['features'], dtype=torch.float32)
    if x.ndim == 1: x = x.unsqueeze(0)
    if x.ndim != 2 or x.shape[1] != 12 or len(data['tickers']) != len(x):
        raise ValueError('Expected one ticker per row and exactly 12 ordered features')
    if not torch.isfinite(x).all(): raise ValueError('Non-finite features')
    return data['tickers'], x

def predict_fn(input_data, artifact):
    tickers, x = input_data
    model, checkpoint = artifact
    with torch.no_grad(): output = model(x)
    probabilities = output[:, 0].sigmoid().tolist()
    returns = (output[:, 1]*checkpoint['return_scale'] + checkpoint['return_mean']).tolist()
    results = []
    for ticker, probability, predicted_return in zip(tickers, probabilities, returns):
        signal = int(probability > checkpoint['threshold'])
        results.append(dict(ticker=ticker, predicted_next_day_logreturn=predicted_return,
                            probability_up=probability, signal=signal,
                            position='LONG' if signal else 'CASH',
                            decision_threshold=checkpoint['threshold']))
    return results

def output_fn(prediction, accept):
    if accept.split(';')[0] != 'application/json': raise ValueError('Expected application/json')
    return json.dumps({'predictions': prediction}, allow_nan=False)
