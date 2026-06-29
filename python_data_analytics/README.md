# Retail Data Analytics

## Introduction
This project delivers an end-to-end data analytics solution for London Gift Shop and an Online Retail Store. It covers data ingestion from both PostgreSQL and raw CSV sources, exploratory data analysis (EDA), anomaly detection using Isolation Forest, demand forecasting using Facebook Prophet, and customer segmentation using RFM analysis. The work is organized across two Jupyter notebooks, each focusing on a different dataset.

## Quick Start
```bash
# Start the PostgreSQL Docker container (if loading data from PSQL)
./scripts/psql_docker.sh start

# Launch Jupyter notebook environment
docker run -p 8888:8888 jarvis-jupyter

# Connect both containers to a shared bridge network
docker network create jarvis-net
docker network connect jarvis-net jarvis-jupyter
docker network connect jarvis-net jarvis-psql

# Install Python dependencies
pip install pandas numpy matplotlib seaborn scikit-learn prophet sqlalchemy psycopg2-binary kagglehub
```

## Implementation

The project is split into two notebooks that cover different datasets.

### Notebook 1  Retail Data Wrangling and Analytics (`retail_data_analytics_wrangling.ipynb`)

Focuses on data ingestion, cleaning, and core business metric visualization using the Online Retail II dataset. Data is loaded either from a live PostgreSQL table via SQLAlchemy or directly from a CSV file that required column renaming and type casting before analysis.

**Analytics Covered**

- **Total Invoice Amount Distribution**  Histogram and boxplot of invoice amounts; filtered to the 85th percentile to reduce skew from outliers. Includes mean, median, mode, min, and max annotations.
- **Monthly Placed and Canceled Orders**  Bar chart comparing order placements vs. cancellations per month. Canceled orders are identified by invoice codes prefixed with `C`.
- **Monthly Sales**  Line chart of total revenue per month.
- **Monthly Sales Growth**  Month-over-month percentage change in revenue, plotted with a zero-reference line.
- **Monthly Active Users**  Unique customer count per month.
- **New vs. Existing Users**  Stacked bar chart classifying customers by whether their purchase falls in their first-ever purchase month or a subsequent one.

### Notebook 2  Online Sales Dataset Analysis (`OnlineSalesDatasetAnalysis.ipynb`)

Covers a broader multi-year synthetic dataset downloaded via the Kaggle API. It adds derived revenue fields, anomaly detection, demand forecasting, and customer segmentation on top of the EDA layer.

**Data Preparation**

- Parses invoice dates and derives `Year`, `Month`, `YearMonth`, `Week`, and `DayOfWeek` columns
- Computes `GrossRevenue`, `DiscountAmount`, `NetRevenue`, and `IsReturned` flags
- Drops rows with zero or negative quantity/price values and produces a data quality summary

**Analytics Covered**

- **Revenue by Category**  Bar chart and pie chart of net revenue share across product categories
- **Monthly Revenue Trend**  Line chart with area fill showing net revenue over time
- **Revenue by Category Over Time**  Stacked area chart with year-start and February markers highlighting seasonal dips
- **September Seasonality Analysis**  Daily-average revenue by month alongside a per-year September revenue breakdown that isolates a 2022 anomaly
- **Sales Channel Analysis**  Net revenue and return rate comparison between online and in-store channels
- **RFM Customer Segmentation**  Customers scored on Recency, Frequency, and Monetary value and assigned to segments: Champions, Loyal Customers, Recent Customers, At Risk, Can't Lose Them, Needs Attention, and Lost

**Machine Learning**

- **Anomaly Detection (Isolation Forest)**  Trains on monthly aggregated features (daily revenue, daily orders, daily customers, average order value, average discount, average unit price, and month) with `contamination=0.1`. Flags low-revenue anomalies, confirming the September 2022 outlier identified during EDA.
- **Demand Forecasting (Facebook Prophet)**  Trains a separate Prophet model per product using monthly quantity data. Uses multiplicative yearly seasonality and holds out the last 3 months for evaluation. Reports MAE and RMSE per product.
- **Restock Recommendations**  For any target month, generates a recommended restock quantity per product with volatility-adjusted min/max bounds derived from each product's coefficient of variation (CV). Results are plotted as horizontal bar charts with error bars.

### Architecture

```
CSV / PostgreSQL
      ¦
      ?
Pandas DataFrame  --?  Cleaning & Feature Engineering
      ¦
      +--? EDA (distributions, trends, segmentation)
      ¦
      +--? Isolation Forest  --?  Anomaly Flags
      ¦
      +--? Facebook Prophet  --?  Restock Recommendations
```

### Scripts / Notebooks

**`retail_data_analytics_wrangling.ipynb`**  Data ingestion (PSQL + CSV), type casting, and six core business metric visualizations. Entry point for understanding the raw transaction data.

**`OnlineSalesDatasetAnalysis.ipynb`**  Full EDA pipeline including anomaly detection, RFM segmentation, and Prophet-based demand forecasting with restock output. Entry point for ML-driven insights and inventory planning.

### Database Schema (PSQL source)

| Column | Description |
|---|---|
| Invoice | Invoice number; prefixed with `C` for cancellations |
| StockCode | Product code |
| Description | Product name |
| Quantity | Units per transaction |
| InvoiceDate | Transaction timestamp |
| Price | Unit price |
| CustomerID | Unique customer identifier |
| Country | Customer country |

## Testing
Each notebook was validated by running all cells end-to-end and inspecting outputs at each stage:
- Schema and null audits were run before any transformation to catch data quality issues early
- Distribution and trend plots were cross-checked against raw `groupby` outputs to confirm aggregation correctness
- Isolation Forest anomaly flags were verified against the September 2022 pattern identified manually during EDA
- Prophet forecasts were evaluated against a held-out 3-month test set; per-product MAE and RMSE were reviewed to confirm reasonable fit before using the models for restock inference

## Improvements
- **Live Data Pipeline**  Replace the static CSV ingestion with a scheduled pipeline pulling directly from the PostgreSQL source to keep analytics current
- **Expanded Anomaly Features**  Add return rate and shipping cost signals to the Isolation Forest feature set for richer anomaly context
- **Forecast Horizon Extension**  Extend Prophet forecasting beyond one month at a time and add confidence interval visualization over a rolling 6-month window
- **Dashboard**  Expose key metrics and restock recommendations through an interactive dashboard (e.g., Streamlit or Dash) for business stakeholder access without needing to run the notebooks directly