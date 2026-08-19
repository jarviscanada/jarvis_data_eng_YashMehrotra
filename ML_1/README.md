# Home Credit Default Risk Modeling

## Introduction

This project develops an end-to-end machine learning workflow for predicting the probability that a Home Credit applicant will experience payment difficulty. Using the Home Credit Default Risk dataset, the project covers exploratory data analysis, preprocessing, feature engineering, customer segmentation, model comparison and hyperparameter tuning, holdout validation, SHAP-based explainability, model governance, and population-stability monitoring.

The workflow is organized across five Jupyter notebooks. Application data is combined with aggregated bureau history to create a feature table for credit-risk modeling. Multiple classification approaches are evaluated using ranking, discrimination, calibration, and threshold-based metrics, and the selected model is validated on an untouched stratified holdout set. The final explainability stage produces global and applicant-level SHAP explanations, adverse-action reasons, subgroup diagnostics, and a monitoring dashboard.

## Quick Start

The project is designed to run as an ordered notebook pipeline through `run_pipeline.py`. The pipeline validates that the notebooks and required stage inputs are present before execution, then runs each selected notebook with Jupyter `nbconvert`.

```bash
# Create the expected project directories if they do not already exist
mkdir -p data models reports

# Place the required Home Credit source files in data/
# data/application_train.csv
# data/bureau.csv

# Install the main Python dependencies
pip install pandas numpy matplotlib seaborn scikit-learn xgboost shap pyarrow joblib jupyter

# Run the complete pipeline from EDA through explainability
python run_pipeline.py
```

By default, the pipeline executes these stages in dependency order:

```text
01_eda.ipynb
    ↓
02_preprocessing.ipynb
    ↓
03_feature_engineering.ipynb
    ↓
04_modeling.ipynb
    ↓
05_explainability.ipynb
```

The runner can also execute only part of the workflow when upstream artifacts already exist:

```bash
# Run preprocessing through modeling
python run_pipeline.py \
  --from-stage 02_preprocessing.ipynb \
  --to-stage 04_modeling.ipynb

# Run only the explainability stage
python run_pipeline.py \
  --from-stage 05_explainability.ipynb \
  --to-stage 05_explainability.ipynb

# Disable the default 1200-second per-cell timeout
python run_pipeline.py --timeout -1

# Execute notebooks without overwriting their saved outputs
python run_pipeline.py --no-inplace
```

The pipeline stops immediately if a required input is missing or if any notebook fails, preventing downstream stages from running on incomplete artifacts.

## Implementation

### Pipeline Runner (`run_pipeline.py`)

`run_pipeline.py` is the main orchestration entry point for the project. It treats the five notebooks as ordered pipeline stages and executes them with the same Python environment used to launch the script.

The runner provides the following controls:

- **Ordered execution** — stages are executed from EDA through explainability in a fixed dependency sequence.
- **Partial pipeline runs** — `--from-stage` and `--to-stage` allow individual stages or contiguous subsets of the workflow to be rerun.
- **Input validation** — before execution, the runner checks that the selected notebooks and the required inputs for the first selected stage are available.
- **Dependency validation** — when feature engineering is included, `bureau.csv` is explicitly required because bureau aggregation is part of that stage.
- **Failure handling** — a notebook failure stops the pipeline and returns the failed process exit code. Configuration problems return exit code `2`.
- **Notebook persistence control** — notebooks execute in place by default, while `--no-inplace` runs them without replacing their stored outputs.
- **Configurable execution timeout** — `--timeout` controls the Jupyter per-cell timeout and defaults to 1200 seconds.

The stage-specific prerequisites enforced by the runner are:

| Starting Stage | Required Inputs |
|---|---|
| `01_eda.ipynb` | `data/application_train.csv`, `data/bureau.csv` |
| `02_preprocessing.ipynb` | `data/application_train.csv` |
| `03_feature_engineering.ipynb` | `data/application_train_clean.parquet`, `data/split_assignments.parquet`, `data/bureau.csv` |
| `04_modeling.ipynb` | `data/application_features.parquet`, `data/split_assignments.parquet`, `data/feature_dictionary.json` |
| `05_explainability.ipynb` | `data/application_features.parquet`, `data/split_assignments.parquet`, `models/credit_scoring_feature_pipeline.pkl`, `models/model_metadata.json` |

### Shared Python Modules (`src/credit_risk`)

Reusable transformations and evaluation logic are separated from notebook orchestration under `src/credit_risk/` so the same deterministic logic can be reused by training notebooks and future inference code.

- **`preprocessing.py`** — normalizes known Home Credit data issues by converting the `DAYS_EMPLOYED = 365243` sentinel to missing, retaining a `DAYS_EMPLOYED_SENTINEL` indicator, and replacing `CODE_GENDER = XNA` with missing.
- **`features.py`** — creates deterministic application-level ratios and summary features and aggregates bureau account history to one row per applicant.
- **`metrics.py`** — calculates the F1-optimal probability threshold and evaluation metrics including AUROC, Gini, KS, AUPRC, F1, and Brier score.
- **`__init__.py`** — exposes the reusable cleaning, feature-engineering, bureau-aggregation, and metric functions as the package interface.

### Notebook 1 - Exploratory Data Analysis (`01_eda.ipynb`)

The first notebook establishes the structure, quality, imbalance, and major risk patterns in the Home Credit application data.

**Analysis Covered**

- Audits row counts, data types, duplicate applicants, and missing values
- Reviews features with high missingness and investigates whether missingness itself may carry predictive signal
- Examines the class imbalance in `TARGET`
- Identifies known sentinel and suspicious values, including `DAYS_EMPLOYED = 365243`
- Visualizes distributions of important numeric variables such as applicant age, income, requested credit, annuity, and goods price
- Compares default rates across customer and application segments
- Examines numeric relationships with `TARGET`
- Studies the three external credit-score variables and their relationship with default risk
- Loads `bureau.csv` to inspect applicants' previous credit-history coverage

### Notebook 2 - Data Preprocessing (`02_preprocessing.ipynb`)

The preprocessing notebook converts known data-quality issues into consistent model-ready representations and creates a fixed train/holdout split used by downstream notebooks.

**Data Cleaning**

- Replaces the `DAYS_EMPLOYED` sentinel value `365243` with missing values
- Adds `DAYS_EMPLOYED_SENTINEL` so the original anomaly remains observable
- Converts `CODE_GENDER = XNA` to missing while retaining `ORGANIZATION_TYPE = XNA` as a potentially meaningful category
- Retains high-missingness property fields provisionally rather than deleting them automatically
- Adds missing-value indicators for features exceeding the configured missingness threshold
- Uses a logistic regression diagnostic to test whether overall missingness patterns contain target signal
- Reviews highly correlated numeric feature pairs to reduce unnecessary redundancy

**Preprocessing Pipeline**

- Numeric values: median imputation and standard scaling
- Categorical values: most-frequent imputation and one-hot encoding
- Unknown categories: ignored safely by the encoder
- Fixed stratified train/holdout assignments are persisted for consistent evaluation across later notebooks

**Saved Outputs**

- `data/application_train_clean.parquet`
- `data/split_assignments.parquet`

### Notebook 3 - Feature Engineering (`03_feature_engineering.ipynb`)

The feature-engineering notebook creates interpretable application-time credit-risk features and aggregates bureau history to applicant level.

**Application Features**

Derived variables include:

- `AGE_YEARS`
- `EMPLOYMENT_YEARS`
- `CREDIT_INCOME_RATIO`
- `ANNUITY_INCOME_RATIO`
- `CREDIT_TERM_PROXY`
- `EMPLOYMENT_AGE_RATIO`
- `INCOME_PER_PERSON`
- `CREDIT_GOODS_RATIO`
- External-score mean, standard deviation, minimum, maximum, and missing-count features
- Age buckets
- Document count
- Contactability score

These features normalize credit exposure and repayment burden relative to applicant resources while converting day-offset fields into more interpretable units.

**Bureau Aggregation**

The bureau dataset is aggregated from account-level records to the applicant level and joined to the application feature table. The resulting variables summarize previous credit-history coverage and add a `BUREAU_HISTORY_MISSING` indicator when no bureau history is available.

**Customer Segmentation**

K-Means clustering is used as an unsupervised business-analysis layer. Candidate cluster counts are compared using inertia and silhouette score. The clustering preprocessing and centroids are fitted only on training rows, then used to assign segments to the complete dataset. `TARGET` is used only afterward to profile the resulting segments rather than to construct them.

The current saved cluster-selection report gives the highest tested silhouette score at **k = 2** (`0.1755`).

**Saved Outputs**

- `data/application_features.parquet`
- `data/preprocessed_train.csv`
- `data/feature_dictionary.json`
- `models/customer_segmentation_bundle.pkl`
- `reports/customer_segmentation_k_selection.csv`
- `reports/customer_segment_profiles.csv`

The resulting feature table contains **307,511 applicants and 198 columns**.

### Notebook 4 - Modeling (`04_modeling.ipynb`)

The modeling notebook trains, compares, tunes, and validates credit-risk classifiers while preserving the fixed untouched holdout set.

**Dataset Split**

- Training population: **246,008 applicants**
- Holdout population: **61,503 applicants**
- Development and validation sets are created from the training population using stratification

Sensitive or governance-oriented variables such as `CODE_GENDER` and `NAME_FAMILY_STATUS` are excluded from supervised decisioning. The human-readable customer-segment label is also excluded.

**Baseline Models**

The saved comparison report evaluates:

| Model | AUROC | AUPRC | F1 |
|---|---:|---:|---:|
| Gradient Boost | 0.7557 | 0.2440 | 0.3041 |
| Logistic Regression | 0.7474 | 0.2249 | 0.2965 |
| Random Forest | 0.7372 | 0.2166 | 0.2857 |
| Dummy | 0.5000 | 0.0807 | 0.1494 |

Gradient Boost is selected from the current baseline comparison and tuned using `RandomizedSearchCV` with three-fold `StratifiedKFold` cross-validation and AUROC as the optimization metric.

**Customer-Segment Ablation**

The supervised model is evaluated both with and without the K-Means customer-segment feature. The saved validation report shows:

- With customer segment: **0.75880 AUROC**
- Without customer segment: **0.75883 AUROC**

Because the segment does not improve validation AUROC, it is retained for descriptive business analysis but excluded from the supervised decision model.

**Cross-Validation**

The final selected pipeline is evaluated with five-fold stratified cross-validation. The saved folds achieve AUROC values from approximately **0.7628 to 0.7652**, demonstrating consistent ranking performance across folds.

**Holdout Evaluation**

The current saved holdout report records:

| Metric | Holdout Score |
|---|---:|
| AUROC | 0.7685 |
| Gini | 0.5371 |
| KS | 0.3994 |
| AUPRC | 0.2609 |
| F1 | 0.3179 |
| Brier Score | 0.1876 |
| Decision Threshold | 0.6885 |

The notebook also produces a classification report, confusion matrix, ROC/precision-recall analysis, calibration diagnostics, and subgroup governance metrics.

**Saved Outputs**

- Final model bundle under `models/`
- Model metadata under `models/`
- `reports/model_comparison.csv`
- `reports/cross_validation_scores.csv`
- `reports/customer_segment_model_uplift.csv`
- `reports/model_governance_subgroup_audit.csv`

### Notebook 5 - Model Explainability (`05_explainability.ipynb`)

The final notebook evaluates how the trained model reaches its predictions and creates artifacts suitable for model review and monitoring.

**Explainability and Governance**

- Computes global SHAP values on a sample of holdout applicants
- Produces SHAP beeswarm and feature-importance plots
- Builds local waterfall explanations for high-risk, borderline, and low-risk applicants
- Generates applicant-level predicted probabilities and approve/decline decisions using the stored model threshold
- Produces an example adverse-action notice based on the largest positive SHAP contributions
- Audits performance and outcomes across governance subgroups

**Population Stability**

Population Stability Index (PSI) is calculated for the leading SHAP features by comparing the training and holdout feature distributions.

The notebook classifies PSI results using the following monitoring thresholds:

- **PSI < 0.10** — Stable
- **0.10 ≤ PSI < 0.25** — Moderate shift
- **PSI ≥ 0.25** — Significant shift

**Monitoring Dashboard**

The notebook combines validation AUROC, leading SHAP feature importance, and PSI into a model-monitoring dashboard saved as:

```text
reports/model_monitoring_dashboard.png
```

**Saved Outputs**

- `reports/holdout_financial_metrics.csv`
- `reports/cross_validation_scores.csv`
- `reports/shap_feature_importance.csv`
- `reports/adverse_action_notice.csv`
- `reports/population_stability_index.csv`
- `reports/model_monitoring_dashboard.png`
- SHAP values under `models/`

## Architecture

```text
                         run_pipeline.py
                               |
                  validates inputs and stages
                               |
                               v
                    01_eda.ipynb
                               |
                               v
               02_preprocessing.ipynb
                       |
                       +----> application_train_clean.parquet
                       +----> split_assignments.parquet
                               |
                               v
             03_feature_engineering.ipynb
                |                         ^
                |                         |
                +---- application data   +---- bureau.csv
                |                               aggregated with
                |                               src/credit_risk/features.py
                v
                application_features.parquet
                feature_dictionary.json
                customer segmentation artifacts
                               |
                               v
                   04_modeling.ipynb
                |
                +----> model comparison and tuning
                +----> stratified cross-validation
                +----> holdout evaluation
                |
                v
          credit_scoring_feature_pipeline.pkl
                 model_metadata.json
                               |
                               v
                05_explainability.ipynb
                |
                +----> SHAP explanations
                +----> adverse-action reasons
                +----> subgroup governance audit
                +----> population stability index
                |
                v
              monitoring reports/dashboard
```

The notebooks remain the analytical stages of the project, while `run_pipeline.py` provides orchestration and `src/credit_risk/` holds reusable deterministic transformations and evaluation helpers. This keeps pipeline execution, modeling logic, and reusable code separated.

## Project Structure

```text
ML_1/
├── run_pipeline.py
├── src/
│   └── credit_risk/
│       ├── __init__.py
│       ├── preprocessing.py
│       ├── features.py
│       └── metrics.py
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modeling.ipynb
│   └── 05_explainability.ipynb
├── data/
│   ├── application_train.csv
│   ├── bureau.csv
│   └── generated parquet / feature artifacts
├── models/
│   └── trained model, segmentation, metadata, and SHAP artifacts
├── reports/
│   ├── model_comparison.csv
│   ├── cross_validation_scores.csv
│   ├── customer_segment_model_uplift.csv
│   ├── customer_segment_profiles.csv
│   ├── customer_segmentation_k_selection.csv
│   ├── holdout_financial_metrics.csv
│   ├── model_governance_subgroup_audit.csv
│   ├── population_stability_index.csv
│   ├── shap_feature_importance.csv
│   └── model_monitoring_dashboard.png
└── documentation/
    └── supporting course and finance documentation
```

The raw `data/` inputs are expected locally. Intermediate data, trained-model artifacts, and reports are produced by the pipeline stages and become prerequisites for downstream stages.

## Testing and Validation

The project uses pipeline-level checks and model-validation layers rather than relying on a single model score:

- `run_pipeline.py` validates notebook availability before starting execution
- Stage-specific input files are checked before the first selected stage is run
- Invalid stage ranges are rejected when `--from-stage` comes after `--to-stage`
- Any notebook execution failure immediately stops downstream processing

- Data-quality and sentinel audits are performed before feature construction
- Fixed stratified split assignments ensure the holdout population is not reused during model development
- Development/validation splitting is stratified to preserve the low default rate
- Candidate models are compared against a dummy baseline using AUROC, Gini, KS, AUPRC, F1, Brier score, and runtime
- Hyperparameters are selected using stratified cross-validation
- Five-fold cross-validation checks stability of the selected pipeline
- Customer segmentation is retained in supervised modeling only if it improves validation AUROC
- Final performance is measured on the untouched holdout set
- Calibration and confusion-matrix diagnostics evaluate probability and threshold behavior
- SHAP explanations verify global and local model drivers
- Governance reports compare model behavior across excluded demographic/group attributes
- PSI checks whether important feature distributions have shifted between development and holdout populations

## Limitations

- Results reflect the historical population represented by the source dataset and may not generalize to different products, geographies, underwriting policies, or economic conditions.
- Bureau coverage and external-score missingness can change between populations and should be monitored in deployment.
- Model discrimination does not by itself establish fairness, regulatory compliance, or suitability for automated lending decisions.

## Improvements

- **Automated Pipeline Tests** — Add unit and integration tests for cleaning rules, feature calculations, schema expectations, model serialization, and inference consistency.
- **Experiment Tracking** — Add MLflow or an equivalent experiment registry for parameters, metrics, artifacts, lineage, and model versioning.
- **Production Monitoring** — Automate monthly AUROC, AUPRC, KS, Brier score, calibration, PSI, approval rates, and subgroup outcome reporting.
- **Retraining Policy** — Define explicit triggers for data drift, performance deterioration, calibration shift, or policy changes that require model review and retraining.
