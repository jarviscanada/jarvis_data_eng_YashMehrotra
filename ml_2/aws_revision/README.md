# AWS FFNN revision

Upload train.py and inference.py to /home/sagemaker-user/stock-ml/src/ in SageMaker. Use the supplied notebooks in place of the older copies.

1. Run train.ipynb in order. Stop if training fails its validation gate. It uses the existing already-scaled training and validation CSVs. Do not scale these twice.
2. Run inference.ipynb in order. Packages are stored under models/ffnn-v2/ so the previous artifact remains available. It creates stock-ffnn-direction-v2. Point the Step Functions batch transform ModelName to that model after review.
3. Inspect the added full-test evaluation cell. Test results are a final audit, not a way to tune thresholds. The latest-row payload is only a snapshot.
4. Keep the existing Glue feature engineering and training scaler. The Lambda still reads signal and predicted_next_day_logreturn. signal now comes from the probability head and need not agree with the auxiliary return head's sign. probability_up and decision_threshold are additional output fields; Lambda can retain them if desired.

Training compares three fixed seeds using validation balanced accuracy. Each model trains two heads: class-weighted binary cross entropy for the sign of next-day return, plus a lightly weighted standardized return regression loss. Smaller layers and much weaker regularization replace the older heavily regularized model. A validation-selected threshold is stored inside the checkpoint. Deployment fails if the best validation balanced accuracy is below 0.505 or either signal is absent. This does not guarantee either signal on any particular live day and does not establish profitability. Evaluate turnover and costs before use.

The serving script rejects old checkpoints explicitly. A newly trained classifier cannot use the old weights. No changes have been deployed to AWS by this revision.
