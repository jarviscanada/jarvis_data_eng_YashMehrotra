CREATE OR REFRESH STREAMING TABLE stock_bronze
COMMENT 'Raw stock price data loaded from the ingestion table'
AS
SELECT
    ticker,
    trade_date,
    open,
    high,
    low,
    close,
    volume,
    ingested_at
FROM STREAM(workspace.stock_project.raw_stock_prices);


CREATE OR REFRESH STREAMING TABLE company_bronze
COMMENT 'Raw company information loaded from the ingestion table'
AS
SELECT
    ticker,
    company_name,
    description,
    exchange,
    currency,
    country,
    sector,
    industry,
    market_capitalization,
    pe_ratio,
    dividend_yield,
    week_52_high,
    week_52_low,
    ingested_at
FROM STREAM(workspace.stock_project.raw_company_info);