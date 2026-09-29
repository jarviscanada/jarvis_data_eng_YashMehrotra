# Step 5 Image Pilot Decision

**Decision: do not promote to paper trading.**

The complete experiment used 50,622 daily 30-session charts across ten stocks and trained the documented fine-tuned ResNet-18 for all 15 epochs. Fine-tuned ResNet-18 produced 55.1% accuracy and 0.508 AUC; frozen ResNet features with logistic regression produced 54.6% accuracy and 0.512 AUC. The positive-label base rate was 56.0%.

The net five-day Sharpe values are not sufficient evidence of predictive edge because a predominantly long policy benefits from the market's upward drift. Promotion requires at least 0.55 AUC on a future temporal holdout, accuracy above the base-rate classifier, and positive performance after costs.

The image pilot remains a research challenger. It is not part of the next-day feedforward deployment package.
