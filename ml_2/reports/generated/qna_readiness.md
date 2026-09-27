# Module 2 Deep Learning Project Q&A Guide

This guide answers the Module 2 question bank using results recorded in the notebooks and project reports. It also identifies ideas that were discussed but not implemented in the current run.

## Project Overview

### Walk me through your deep learning project.

I built a stock-return research pipeline for 50 US equities covering 2005 through 2025, with safeguards against time-series leakage. It includes EDA, trailing feature engineering, a feedforward network, an LSTM, a ResNet-18 chart-image pilot, and a long-or-cash backtest with transaction costs. The feedforward model achieved 52.08% directional accuracy, a 1.17 net Sharpe ratio, and a 15.36% annualized return on the untouched test period. It trailed SPY, so I would test it in paper trading rather than use live capital.

### You have five minutes. What did you build, and what did you find?

I built a reproducible research and inference package with chronological splits, training-only scaling, saved model artifacts, comparable baselines, and a net-of-costs backtest. The feedforward model slightly improved MSE over linear regression and materially reduced turnover, while the LSTM did not improve the final business result. The image pilot produced about 55% accuracy but only 0.508 to 0.512 AUC against a 56% positive-class base rate, so it was not promoted. The main finding is that model complexity did not reliably beat disciplined tabular modeling or the market benchmark.

### Why deep learning at all? They already had a linear model. What made you think a neural network would find something it could not?

The hypothesis was that nonlinear interactions among momentum, volatility, volume, trend, and VIX features might matter even when each feature has weak marginal predictive power. That justified testing a regularized network, not assuming it would win. The final MSE difference was small, so the evidence supports cautious experimentation rather than a claim that deep learning was necessary.

### What was the hardest part?

The hardest technical problem was temporal alignment: every feature had to be available at the decision date, every target had to occur afterward, split-crossing labels had to be purged, and all models had to be evaluated on identical endpoints. That work mattered more than increasing model size because a small alignment error could create a convincing but false result.

### What is the weakest part of this work?

The weakest part is statistical robustness. The training runs use one random seed, overlapping sequence windows are not converted into corrected confidence intervals, and performance is not formally segmented by market regime. Those limitations are why the recommendation stops at paper trading.

### What surprised you?

The LSTM used 53,313 parameters and slightly higher directional accuracy than the feedforward model, yet it had worse MSE and lower net Sharpe. The 120-day window also had the best validation MSE in the length sweep, but only narrowly. These results suggest that additional temporal capacity mostly modeled noise rather than a stable trading edge.

### What would you do differently if you started again?

I would pre-register a multi-seed protocol, block-bootstrap the economic metrics, define volatility and trend regimes before model selection, and build the shared feature-engineering module before training. I would also reserve a second untouched temporal holdout for the final governance decision.

## Follow-up Challenges

### I think your result is too good. Convince me it is real.

The result is not presented as extraordinary: the strategy underperformed SPY in return and Sharpe. Leakage controls include per-ticker features, chronological non-overlapping date splits, train-only scaler fitting, purged split-crossing targets, one final test evaluation for the registered primary, transaction costs, and a linear baseline. I would still require paper-trading replication because one historical test cannot prove a durable edge.

### Suppose I tell you there is a leak somewhere in this pipeline. Where do you look first, second and third?

First I inspect target alignment and confirm that the row dated t predicts the return from t to the next trading date. Second I inspect rolling features, scaling, and VIX joins to ensure they use only data available at t and that the scaler saw training rows only. Third I inspect split boundaries and sequence construction for windows or outcomes that cross from training into validation or test.

### What is the strongest argument against your own recommendation?

The strategy trails SPY, may contain survivorship bias, and has not been validated across seeds or in live operations. Even paper trading consumes attention and infrastructure, so the strongest counterargument is that the small incremental modeling evidence does not justify deployment effort.

## Data Targets and Leakage

### What is data leakage? Name three ways it gets into a pipeline.

Leakage is information available only after the prediction time entering training or model selection. Three common routes are fitting preprocessing on all dates, building rolling features with future observations, and repeatedly selecting models against the final test set. Split-crossing forward labels are another important route in this project.

### What is the difference between a validation set and a test set, and why do you need both?

Validation data supports choices such as architecture, stopping epoch, and sequence length. Test data estimates performance only after those choices are fixed. Without both, model selection gradually overfits the same supposedly unseen observations.

### What does it mean for a time series to be stationary, and why do most models assume it?

A stationary series has a distribution whose key properties are stable over time. Models rely on that stability because they learn past relationships and apply them later. Prices are strongly nonstationary, so this project models log returns and normalized indicators, but it does not claim or formally prove complete stationarity.

### Describe how you constructed your target. Be precise about which day is which.

For a row dated t, the primary target is the next row's per-ticker log return, created with a one-step negative shift. Features are calculated using observations through t; the target is realized on the next trading session. The image pilot separately uses the log return from t to the fifth future trading observation and purges outcomes that cross split boundaries.

### Where were your split boundaries, and what rule set them?

Unique eligible dates were split chronologically at the 70th and 85th percentiles. Training contains 172,673 rows from 2005-10-17 through 2019-11-27, validation contains 38,100 rows from 2019-11-29 through 2022-12-07, and test contains 38,100 rows from 2022-12-08 through 2025-12-22.

### Why not k-fold cross validation? Be specific about what breaks.

Ordinary shuffled k-fold validation lets later observations help train a model evaluated on earlier observations and breaks the deployment chronology. It also scatters overlapping time windows across folds. Expanding-window walk-forward validation preserves order and better represents repeated retraining followed by future evaluation.

### When did you fit the scaler, and on which rows?

The StandardScaler was fitted once on the 172,673 training rows and then applied unchanged to validation and test. Each walk-forward LSTM fold refitted its own scaler using only data before that fold's validation month.

### What observable result would have told you that you had a leak?

Near-perfect validation accuracy, an implausibly tiny error, a large discontinuity between a random split and chronological split, or performance that disappears after shifting features by one day would trigger a leak investigation. In this noisy task, sustained directional accuracy well above roughly 60% would be treated as suspicious before being treated as a discovery.

### Are your training samples independent? What do overlapping 60 day windows do to your error bars?

No. Adjacent LSTM samples share 59 of 60 observations, and market-wide rows share common shocks. Treating them as independent makes naive standard errors too small. I would estimate uncertainty by resampling contiguous date blocks or by reporting performance over non-overlapping periods.

### What is survivorship bias, is it in your data, and in which direction does it push your results?

Survivorship bias occurs when the historical universe is formed from securities that survived or are prominent today, excluding delisted failures. The project acknowledges that it may be present. It generally pushes historical performance upward by omitting weak or failed firms.

### Why log returns rather than simple returns?

Log returns add across time, which makes multi-period aggregation and equity reconstruction convenient. They are also approximately symmetric for small changes. The backtest converts accumulated log returns back to simple wealth with the exponential function.

## Neural Network Fundamentals

### What is an activation function, and why is non-linearity necessary at all?

An activation function transforms a layer's weighted sum. Without a nonlinear activation, multiple linear layers collapse into one linear transformation, so depth cannot represent nonlinear feature interactions. This project uses ReLU between hidden layers.

### What is the difference between an epoch, a batch and an iteration?

An epoch is one complete pass over the training set. A batch is the subset processed together. An iteration is one optimizer update, so an epoch contains approximately the number of training rows divided by the batch size iterations.

### What is the difference between a loss function and an evaluation metric?

The loss is the differentiable objective optimized during training; here it is MSE. Evaluation metrics describe behavior we care about, including MAE, directional accuracy, Sharpe ratio, drawdown, and turnover. A model can improve loss without improving the business metrics.

### Why does stacking linear layers without activation functions not give you a deeper model?

The product and sum of affine transformations is another affine transformation. Therefore several linear layers without nonlinear activations have the same representational class as one linear layer.

### Why did your output layer have no activation function?

The target is an unrestricted real-valued next-day log return. A final sigmoid would constrain it to zero through one and a tanh would constrain it to minus one through one, changing the regression problem and potentially saturating gradients.

### Why is mean squared error a questionable choice when returns are fat tailed?

MSE squares residuals, so a few extreme returns can dominate the gradient. It is useful and conventional, but Huber loss or MAE would be more robust. The project reports MAE alongside MSE but did not retrain with a robust loss, which is a follow-up experiment.

### Roughly how many parameters did your best model have, and how did that compare to your number of training rows?

The feedforward model had 12,481 trainable parameters and 172,673 training rows, about 13.8 rows per parameter. That ratio does not guarantee generalization because the rows are correlated, but it is much less extreme than having more parameters than observations.

### What happens if your learning rate is a hundred times too high? A hundred times too low?

At 0.1 instead of 0.001, updates would likely overshoot, oscillate, or produce NaNs. At 0.00001, training would progress very slowly and could appear underfit within the epoch budget. The project used 0.001 for tabular models and 0.0001 for fine-tuning but did not run this exact ablation.

### What does Adam do that plain stochastic gradient descent does not?

Adam maintains moving estimates of each parameter's first and second gradient moments, giving adaptive per-parameter step sizes with momentum-like behavior. Plain SGD applies the same global learning rate unless momentum or another extension is added.

### Explain the bias variance trade-off on a dataset this noisy.

A simple model can miss genuine nonlinear structure, which is high bias. A large model can fit unstable market noise, which is high variance. Validation, regularization, baselines, and out-of-time testing are used to find a useful middle ground; the LSTM result shows that more capacity did not automatically improve generalization.

## Implementation

### What is a tensor, and how does it differ from a NumPy array?

A tensor is a multidimensional numeric array with device placement and automatic-differentiation support. A NumPy array is primarily a CPU data structure and does not build a gradient graph. PyTorch tensors can run on a GPU and participate directly in backpropagation.

### What is automatic differentiation, and why does a deep learning framework need it?

Automatic differentiation records tensor operations and applies the chain rule backward to calculate gradients. It lets the framework obtain derivatives for thousands of parameters without manually deriving each equation.

### What is the optimizer responsible for, and how is that different from the loss function?

The loss measures how wrong the current predictions are. The optimizer uses gradients of that loss to update parameters. Changing the optimizer changes the update rule, while changing the loss changes the objective.

### Describe the five steps of a PyTorch training loop, in order.

Set training mode and load a batch; clear old gradients; run the forward pass and compute loss; call backward to calculate gradients; then call the optimizer step. The project also clips LSTM gradients and evaluates validation loss in evaluation mode after each epoch.

### What does model.eval() change, and what breaks silently if you forget it?

`model.eval()` makes dropout deterministic by disabling random masks and makes batch normalization use stored running statistics. Forgetting it makes predictions random and lets batch composition change outputs, silently corrupting validation and inference.

### Which of your data loaders shuffled and which did not? Justify the difference.

Training loaders shuffle complete samples so optimizer batches are better mixed. Validation and test loaders do not shuffle because deterministic ordering simplifies alignment with dates and tickers. Sequence order inside each LSTM sample is never shuffled.

### What shape does an LSTM input tensor have, and what does each dimension mean?

With `batch_first=True`, the shape is batch size by sequence length by feature count. The primary experiment used batches of 128, 60 trading days, and 12 features.

### What do you have to save besides the model weights in order to make a prediction tomorrow?

I need the exact feature list and ordering, the fitted training scaler, model architecture metadata, threshold or decision rule, preprocessing formulas, and model version. The project saves the checkpoint, feature list, scaler, manifest, and shared inference code.

### A single new row of raw market data arrives. Walk me through every step to a prediction.

A single row is not sufficient by itself because the model uses rolling indicators up to 200 sessions. I append it to validated per-ticker OHLCV history, join contemporaneously available VIX data, calculate trailing features without future data, select the latest complete row, apply the saved training scaler, load the registered checkpoint in evaluation mode, predict under `no_grad`, and choose long if the prediction is positive. `ReturnPredictionService.score_raw_history` now implements that boundary.

## Training and Debugging

### What is the difference between underfitting and overfitting, and how do you spot each on a loss curve?

Underfitting produces high training and validation loss because the model cannot fit even the training structure. Overfitting produces continuing training improvement while validation loss stalls or worsens. The ResNet fine-tuning curve shows strong overfitting: training loss fell while validation loss rose sharply.

### What is a learning rate schedule, and why would you use one?

A schedule changes the learning rate during training, often reducing it after a plateau so optimization can make smaller late-stage adjustments. This project did not use one; early stopping limited wasted epochs. A plateau scheduler would be a reasonable follow-up.

### What makes a result meaningfully better rather than just numerically better?

The improvement should be stable across seeds and time periods, exceed uncertainty, survive costs, and matter to the business metric. A tiny MSE advantage is not meaningful if Sharpe, drawdown, and operational complexity do not improve.

### How did you decide when to stop training?

The feedforward models used a 100-epoch cap and stopped after 10 validation epochs without improvement. The LSTM used a 50-epoch cap with patience seven. The best validation state was restored rather than retaining the final epoch.

### Your training loss is flat from epoch one. Debug it out loud, in order.

I would verify target and feature variation, inspect a batch's shapes and dtypes, confirm parameters require gradients, check that loss is connected to model outputs, confirm `zero_grad`, `backward`, and `step` run in that order, inspect gradient norms, and then test the learning rate and normalization. Finally I would try to overfit a tiny batch; failure there indicates an implementation problem rather than generalization.

### Your loss becomes NaN at epoch seven. What are the candidate causes, ranked?

First are non-finite inputs or targets, then exploding gradients or an excessive learning rate, followed by unstable divisions or logarithms in preprocessing, mixed-precision overflow, and corrupted optimizer state. I would capture the first bad batch, assert finiteness, inspect gradient norms, lower the learning rate, and use clipping.

### How many random seeds did you run, and what was the spread of your headline metric?

I ran one seed, 42, so I cannot report a seed-to-seed spread or claim that the result is stable across initializations. Before promotion I would run at least five seeds and report the median, range, and confidence interval for MSE, directional accuracy, and net Sharpe.

### How do you distinguish a real improvement from noise?

I would require consistent gains across seeds, expanding time folds, and block-bootstrap intervals, plus improvement after costs on a locked holdout. The current project supports a hypothesis and paper-trading gate, not a claim of statistically proven alpha.

## Regularization

### What is regularization, in one sentence?

Regularization constrains how a model learns so it generalizes better instead of fitting training noise.

### What is the difference between L1 and L2 regularization, and what does each do to the weights?

L1 adds the absolute value of weights and tends to drive some weights exactly to zero. L2 adds squared weights and smoothly shrinks large weights. The feedforward optimizer uses L2-style weight decay of 0.0001, not L1.

### How does dropout work during training, and what changes at test time?

During training, dropout randomly zeros activations and rescales those retained, discouraging reliance on specific paths. During evaluation it is disabled and the full network is used deterministically.

### Name every regularizer in your model and say what each one is doing.

The feedforward model uses 0.3 dropout, L2-style weight decay, batch normalization, validation early stopping, and limited architecture size. Dropout reduces co-adaptation, weight decay discourages large weights, batch normalization stabilizes activations, and early stopping limits fitting after validation stops improving.

### In what order did you place the linear layer, batch norm, activation and dropout? Does the order matter?

Each hidden block is Linear, BatchNorm, ReLU, then Dropout. The order matters because batch normalization is intended to normalize the pre-activation linear output here, and dropout before batch normalization would make the running statistics depend on random masks.

### Why does batch norm behave differently in training and evaluation mode?

During training it normalizes with current-batch statistics and updates running estimates. During evaluation it uses the stored running mean and variance so a prediction does not depend on the other rows in its batch.

### Training loss is high and validation loss is also high. More regularization or less?

That pattern usually indicates underfitting, so I would first reduce regularization or improve features and optimization. I would not automatically enlarge the model until checking data, targets, and learning dynamics.

### How would you augment financial data, and which augmentations are unsafe here?

Reasonable experiments include small price-scale changes when using scale-invariant representations, mild observation noise, or carefully designed temporal cropping that preserves order and labels. Horizontal image flips are unsafe because they reverse time, vertical flips invert price meaning, and arbitrary time shuffling destroys causality. The reported image experiment used deterministic resize and ImageNet normalization, not those unsafe transforms.

## Convolutional Networks

### What is a convolution, and what is parameter sharing buying you?

A convolution slides the same learned filter across positions and produces a response wherever the local pattern occurs. Parameter sharing greatly reduces the number of weights and gives approximate translation equivariance.

### What do kernel size, stride and padding each control?

Kernel size controls the local receptive field, stride controls how far the filter moves between outputs, and padding controls edge treatment and output size.

### What is pooling for, and when would you choose max over average?

Pooling reduces spatial resolution and increases invariance. Max pooling emphasizes whether a strong local feature occurred, while average pooling summarizes overall activation. ResNet uses pooling as part of its standard image hierarchy.

### Explain backpropagation to me in your own words.

The forward pass records how inputs produce a loss. Backpropagation walks those operations in reverse and assigns each parameter responsibility for a small change in that loss. The optimizer then moves parameters in a direction intended to reduce future loss.

### What does a single 1D filter of width five represent on a return series, and how does that relate to a moving average?

It is a learned five-day local pattern detector. A five-day moving average is a special fixed filter with equal coefficients, while a learned convolution can assign different positive or negative weights. This project did not train a 1D CNN; it used an LSTM for numeric sequences and ResNet-18 for chart images.

### Why did you strip the axes and gridlines from the chart images?

Axes, labels, and gridlines are rendering artifacts rather than price behavior and can let a CNN exploit formatting shortcuts. Removing them focuses the representation on candle geometry and volume rather than ticker names, dates, or scale markings.

### Why is a horizontal flip an unsafe augmentation here?

A horizontal flip reverses chronological order, turning cause-before-effect into effect-before-cause while keeping the original label. It creates economically invalid training examples.

### A 1D CNN and an LSTM are both sequence models. When would you prefer each?

A 1D CNN is attractive for local motifs, parallel training, and controlled receptive fields. An LSTM is attractive when ordered state and variable-distance dependencies are central. Given the weak LSTM gain here, a compact 1D CNN would be a useful challenger, not an assumed improvement.

## Recurrent Networks and LSTMs

### What is a recurrent neural network, and how does it differ from a feedforward network?

An RNN processes an ordered sequence while carrying a hidden state from one step to the next. A feedforward network treats each row as a fixed vector and has no learned temporal state.

### What is the difference between an LSTM and a GRU?

An LSTM has separate cell and hidden states with input, forget, and output gates. A GRU combines the state and uses fewer gates and parameters. GRUs can train faster, while LSTMs offer more explicit memory control; this project tested only an LSTM.

### What is the difference between a sequence to one and a sequence to sequence model?

Sequence-to-one maps a complete input window to one output, as this project maps 60 days to one next-day return. Sequence-to-sequence produces an output at multiple or all time steps, such as forecasting an entire future path.

### Why do plain RNNs fail on long sequences, and how does gating fix it?

Repeated multiplication through time can make gradients vanish or explode. LSTM gates create controlled paths that preserve, update, or forget information, allowing gradients and useful state to persist longer.

### What sequence length did you use, and how did you choose it?

The registered LSTM used 60 trading days because that was the specified primary sequence experiment. A later validation sweep found 120 days narrowly best: MSE 0.00055124 versus 0.00055194 for 60 days. Because that sweep occurred after the primary design, 120 days is a future candidate rather than a retroactive test-set replacement.

### What happened when you swept 20, 40, 60 and 120 days? What does that pattern imply about the market?

Validation MSEs were approximately 0.00055578, 0.00055628, 0.00055194, and 0.00055124 respectively. The small differences imply weak, diffuse temporal information rather than a decisive memory horizon. They do not justify claiming a stable 120-day market cycle.

### Why gradient clipping, and what happens without it?

Clipping caps the LSTM gradient norm at 1.0 to limit rare explosive updates. Without it, recurrent gradients can produce unstable steps, oscillation, or NaNs.

### What is walk-forward validation, and why is it better than a single split here?

Walk-forward validation repeatedly trains on an expanding historical window and evaluates the next month. It preserves time order and reveals instability across changing markets; the project ran all monthly folds from the initial 12-month training window through December 2022.

### Your LSTM did not beat the feedforward network. Convince me that is a finding and not a bug.

The LSTM pipeline verifies shapes, uses proper sequence order, training-only fold scaling, gradient clipping, early stopping, and identical test endpoints. It achieved 52.20% directional accuracy, showing it learned something, but its MSE of 0.000303 and net Sharpe of 0.999 were worse than the feedforward model's 0.000298 and 1.171. The plausible conclusion is that the engineered current-state features captured most usable signal and the added sequence capacity increased variance.

## Transfer Learning and Embeddings

### What is transfer learning, and under what conditions does it help most?

Transfer learning reuses representations learned on a source task for a new target task. It helps when the source features are relevant, labeled target data is limited, and the domains are similar enough that early representations transfer.

### Why is an embedding preferable to one-hot encoding for a high cardinality feature?

An embedding learns a compact dense vector in which similar categories can share statistical strength. One-hot encoding is sparse and treats every category as unrelated. This project intentionally did not use ticker embeddings because 50 ticker identities could encourage memorization and weaken out-of-universe generalization.

### What is catastrophic forgetting?

Catastrophic forgetting is the loss of useful pretrained representations when large fine-tuning updates overwrite them. Freezing most ResNet layers and using a small learning rate reduces that risk.

### ResNet-18 was trained on photographs. Why would any of that transfer to a candlestick chart, and what does not transfer?

Early convolutional filters detect generic edges, corners, textures, and shapes that can also appear in chart geometry. High-level ImageNet concepts such as animal or object parts do not directly transfer. The near-random AUC shows that visual transfer did not produce a convincing financial discriminator here.

### Feature extraction or fine tuning? Which did you use, and why?

Both were tested. The feature-extraction approach froze the full backbone and trained logistic regression on 512-dimensional embeddings; the fine-tuning approach trained the final residual block and new classification head. Comparing both tested whether the small domain-specific dataset justified adapting deeper features.

### Why the ImageNet normalization constants specifically? What happens if you skip them?

The pretrained weights were optimized for inputs normalized with ImageNet channel means and standard deviations. Skipping that transformation shifts activation distributions away from what the backbone learned and can reduce transfer performance.

### What stops a per-ticker embedding from simply memorizing individual stocks?

Nothing automatically stops it. Controls would include embedding regularization, validation on unseen dates and unseen tickers, a small embedding dimension, and comparison with a no-identity model. Because the current project did not use ticker embeddings, it avoids that specific memorization route.

## Evaluation and Business Impact

### What is the difference between precision, recall and F1, and when does each matter?

Precision is the fraction of predicted positives that are correct; recall is the fraction of actual positives found; F1 is their harmonic mean. Precision matters when false trades are costly, recall when missed opportunities dominate, and F1 when both matter. The image pilot reported accuracy and AUC, not these class-threshold metrics, so they should be added before promotion.

### What is AUROC, and what does a value of 0.5 mean?

AUROC is the probability that a randomly chosen positive receives a higher score than a randomly chosen negative. A value of 0.5 means ranking is no better than random. The image models produced 0.508 and 0.512, which is insufficient evidence of discrimination.

### What is overfitting to the test set, and how does it happen even when you never trained on it?

It occurs when repeated test evaluation influences model, threshold, or reporting choices. Information can leak through those decisions even if the training code never uses the test data. The feedforward model was fixed before the final comparison, and the challenger results are reported without using them to replace the primary model.

### Your directional accuracy is 54 percent. Is that good?

Not by itself. It must be compared with the class base rate, costs, turnover, confidence intervals, and a naive policy. The primary model is actually 52.08%; the image model's roughly 55% accuracy is below the 56% positive-class base rate and has near-random AUC.

### What accuracy figure would have made you suspect a bug rather than a discovery?

On next-day liquid-equity direction, a stable result above roughly 60% across the full universe would trigger a leak audit before celebration. Extremely high training and validation agreement or a sudden jump after preprocessing would also be suspicious. The exact threshold is a diagnostic rule, not a universal law.

### Walk me through your backtest for a single trading day, step by step.

Using features known at date t, the model predicts each ticker's next-day log return. A positive prediction sets a long position and a nonpositive prediction sets cash. The code compares that position with the prior position, charges 10 basis points per unit change, applies the next-day realized return, averages asset-level net returns equally, and updates cumulative equity and drawdown.

### Where do transaction costs enter, and on what basis are they charged?

Cost equals the absolute asset-level position change multiplied by 10 basis points. Entering long, exiting to cash, or switching after a prior state therefore incurs cost. The cost is subtracted before daily portfolio aggregation.

### What was your turnover, and what did the costs do to your Sharpe ratio?

The feedforward strategy averaged 2.40% daily turnover and recorded 915 position changes. Its Sharpe fell from 1.221 at zero cost to 1.171 at 10 basis points; it remained 1.121 at 20 basis points.

### Your model returned 8 percent annualized and the index returned 12 percent. What is your recommendation?

I would not recommend capital allocation based only on positive absolute return. I would examine risk, drawdown, diversification, and whether it adds value alongside the index. In the actual results, the model returned 15.36% versus SPY's 21.78% and had a lower Sharpe, so the recommendation is limited paper trading for operational validation.

### In which market regimes does your model fail?

The project does not yet provide a formal regime-conditioned scorecard. Walk-forward errors visibly spike around the 2008 crisis and March 2020, suggesting weakness during abrupt high-volatility transitions. That is an informed diagnosis, not a completed regime study, and it is a required follow-up before promotion.

### Explain your best model to a chief investment officer in thirty seconds, with no jargon.

Each day the system combines twelve measures of trend, momentum, volatility, volume, and market fear for 50 stocks. It invests equally in stocks whose next-day return estimate is positive and otherwise holds cash. After estimated trading costs it made money historically but did not beat SPY, so I recommend a monitored paper trial, not live capital.

### Deploy, iterate or abandon? Defend the choice.

Iterate through controlled paper trading. The model has positive net historical performance and a reproducible inference package, but it underperforms SPY and lacks multi-seed, regime, and live-data validation. Abandoning immediately would discard a testable pipeline; deploying live would exceed the evidence.

## Judgment and Communication

### Tell me about a decision in this project you got wrong.

The initial design gave too much weight to model complexity before measuring uncertainty across seeds and regimes. The LSTM and image experiments were useful, but a multi-seed and block-bootstrap protocol would have made every comparison more reliable.

### Your manager tells you your result is wrong. How do you check?

I would ask what failure they suspect, reproduce the run from clean artifacts, and independently verify dates, target shifts, scaler fit rows, model state, prediction alignment, costs, and metric formulas. I would compare a few rows by hand, run invariance tests that deliberately shift dates, and have a second person review the pipeline before defending the result.

### You have one week and a choice of one: more data, better features, or a bigger model. Choose and defend it.

I choose better features and data-quality controls. Larger models already failed to improve the result reliably, while financial signal is limited by noisy inputs, survivorship, and regime change. Better point-in-time fundamentals, corporate-action validation, or cross-sectional features offer a more credible path than additional capacity.

### A portfolio manager tells you he does not trust black boxes. Respond.

That concern is reasonable. I would show the linear baseline, deterministic feature contract, temporal-importance analysis, Grad-CAM diagnostic, turnover and cost decomposition, and explicit failure thresholds. I would also keep the model behind a paper-trading gate with a rollback-to-cash control; trust should come from transparent controls and observed behavior, not from the model label.

## Follow-up Phrase Drill

### If you say I used an LSTM

I used it because a sequence model could learn ordered dependencies beyond the current indicator vector. The registered window was 60 days; a validation sweep found 120 days narrowly best. It did not beat the feedforward model on MSE or net Sharpe, so I conclude that added sequence capacity did not provide a reliable advantage.

### If you say I got 54 percent accuracy

I immediately compare it with the base rate, costs, and uncertainty. The next-day feedforward result was 52.08%, while the image pilot was about 55% against a 56% positive base rate and near-0.5 AUC. Only one seed was run, so I do not claim seed stability.

### If you say it beat the baseline

The baseline was ordinary linear regression using the same 12 scaled features and identical test endpoints. Feedforward MSE was 0.00029750 versus 0.00029843, and net Sharpe was 1.171 versus 0.600. The MSE advantage is small and has not been tested across seeds, so the economic comparison is more notable than the numerical loss gap.

### If you say I backtested it

The policy is equal-weight long-or-cash, formed from next-day predictions on common endpoints. Costs are charged at 10 basis points for each asset-level position change. The primary recorded 915 trades, 2.40% average daily turnover, and a Sharpe reduction from 1.221 before costs to 1.171 after costs.

### If you say I engineered features

The twelve features cover returns, moving-average spreads, RSI, MACD, Bollinger position and width, ATR, volume balance, and VIX. The project has not established which individual feature matters most, so I would not invent that claim; permutation importance by date block is planned. All rolling calculations are trailing and the scaler is fitted on training rows only.

### If you say we decided to

I use “I” for work I completed myself. If a decision or task involved other people, I name their contribution and state my part separately.

### If you say it works

Here, “works” means the pipeline runs reproducibly, produces positive net historical Sharpe under the stated cost model, passes the paper-trading risk gate, and fails closed on invalid inference inputs. Failure would include negative rolling Sharpe, drawdown beyond thresholds, excessive turnover, schema or stale-data errors, or inability to reproduce the holdout result. The monitoring plan is designed to detect those conditions.

## Evidence Index

- `notebooks/01_eda.ipynb`: universe, dates, missing-session audit, return and volatility analysis.
- `notebooks/02_preprocessing.ipynb`: targets, features, split dates, scaling, and dataset shapes.
- `notebooks/03_feedforward_nn.ipynb`: architecture, training, regularization, baselines, and test metrics.
- `notebooks/04_sequence_models.ipynb`: sequence construction, walk-forward folds, temporal gradients, and length sweep.
- `notebooks/05_transfer_learning.ipynb`: image generation, ResNet strategies, AUC, base rate, and Grad-CAM.
- `notebooks/06_backtesting.ipynb`: common-endpoint comparison, costs, benchmark, risk gate, and artifacts.
- `src/features.py` and `src/inference.py`: raw-history feature engineering, saved scaling, and deterministic scoring.
- `reports/generated/model_documentation.md`, `executive_summary.md`, and `monitoring_plan.md`: deployment scope, limitations, decision, and controls.
