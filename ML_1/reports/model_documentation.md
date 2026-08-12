# Home Credit Default Risk Model Validation Summary

## Model purpose

The model ranks Home Credit applicants by the probability of payment difficulty so that credit-review resources and approval thresholds can be applied consistently. It is an educational credit-risk prototype and is not approved for live lending decisions.

## Data and methodology

The development dataset contains 307,511 labeled applications with an 8.07% default rate. A fixed stratified split assigns 246,008 rows to training and 61,503 rows to an untouched holdout set. Application-time ratios, external-score summaries, missingness indicators, and bureau aggregates are created without using TARGET. Customer segments are fitted on training rows only; because the segment reduced validation AUROC by 0.00022, it is retained for business analysis but excluded from supervised decisioning.

Logistic regression, random forest, and XGBoost models were compared. XGBoost won on validation AUROC and AUPRC, then underwent a 50-iteration, three-fold randomized search. The selected configuration uses 500 trees, learning rate 0.10, maximum depth 3, minimum child weight 5, subsample 0.90, column subsampling 0.80, L1 regularization 0.10, and L2 regularization 2.0. Numeric fields use median imputation; nominal categoricals use mode imputation and one-hot encoding. CODE_GENDER, NAME_FAMILY_STATUS, ORGANIZATION_TYPE, and the original NAME_EDUCATION_TYPE category are excluded from decisioning. An ordinal education feature is retained.

## Performance

The feature-table model achieved holdout AUROC 0.7728, Gini 0.5456, KS 0.4043, AUPRC 0.2685, F1 0.3238 at threshold 0.1627, and Brier score 0.0667. Five-fold AUROC was 0.7680 with standard deviation 0.0006, indicating stable ranking performance. The self-contained raw-application production pipeline achieved AUROC 0.7695, Gini 0.5389, and KS 0.4016, closely matching the richer feature-table model while omitting bureau inputs.

## Explainability

Global SHAP analysis on 1,000 random holdout applicants identifies average external credit score, annuity-to-credit term proxy, credit-to-goods ratio, annuity amount, ordinal education level, goods price, and external-score components as the leading drivers. Local waterfall plots cover high-risk, borderline, and low-risk applicants. The sample adverse-action notice reports the four largest positive contributions using applicant-specific values and training benchmarks. Tree SHAP contributions are on the model-margin scale; displayed applicant risks are predicted probabilities.

## Limitations and governance

The split is random because the source data lacks a reliable application timestamp, so temporal recession performance is untested. The dataset represents a historical lending population and may not generalize to another geography, product, or economic period. External-source missingness and bureau coverage may shift in production. Subgroup diagnostics show different observed risk and decline rates across gender and family-status groups even though those attributes are excluded from the model; outcomes therefore require continued fairness and proxy-feature review. The raw production pipeline excludes bureau aggregates and is slightly less discriminative. Probability calibration is acceptable on the current holdout but must be rechecked after any population or policy change.

## Monitoring plan

Monitor monthly AUROC, AUPRC, KS, Brier score, calibration by risk band, approval/decline rates, and subgroup outcomes. Compute PSI for the ten leading SHAP features using the training distribution as reference: PSI below 0.10 is stable, 0.10–0.25 requires investigation, and PSI at or above 0.25 triggers formal model review and potential retraining. Revalidate adverse-action reason mappings whenever features, preprocessing, thresholds, or model parameters change.
