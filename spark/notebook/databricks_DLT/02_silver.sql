CREATE OR REFRESH MATERIALIZED VIEW stock_silver
COMMENT 'Cleaned and typed stock price data'
AS
WITH ranked_prices AS (
    SELECT
        UPPER(TRIM(ticker)) AS ticker,
        CAST(trade_date AS DATE) AS trade_date,
        TRY_CAST(open AS DOUBLE) AS open_price,
        TRY_CAST(high AS DOUBLE) AS high_price,
        TRY_CAST(low AS DOUBLE) AS low_price,
        TRY_CAST(close AS DOUBLE) AS close_price,
        TRY_CAST(volume AS BIGINT) AS volume,
        CAST(ingested_at AS TIMESTAMP) AS ingested_at,

        ROW_NUMBER() OVER (
            PARTITION BY UPPER(TRIM(ticker)), CAST(trade_date AS DATE)
            ORDER BY ingested_at DESC
        ) AS row_num

    FROM stock_bronze

    WHERE ticker IS NOT NULL
      AND trade_date IS NOT NULL
)

SELECT
    ticker,
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    ingested_at
FROM ranked_prices
WHERE row_num = 1
  AND close_price > 0
  AND volume >= 0;


CREATE OR REFRESH MATERIALIZED VIEW company_silver
COMMENT 'Cleaned company data with the latest record per ticker'
AS
WITH ranked_companies AS (
    SELECT
        UPPER(TRIM(ticker)) AS ticker,
        company_name,
        description,
        exchange,
        currency,
        country,
        sector,
        industry,
        TRY_CAST(market_capitalization AS BIGINT)
            AS market_capitalization,
        TRY_CAST(pe_ratio AS DOUBLE)
            AS pe_ratio,
        TRY_CAST(dividend_yield AS DOUBLE)
            AS dividend_yield,
        TRY_CAST(week_52_high AS DOUBLE)
            AS week_52_high,
        TRY_CAST(week_52_low AS DOUBLE)
            AS week_52_low,
        CAST(ingested_at AS TIMESTAMP) AS ingested_at,

        ROW_NUMBER() OVER (
            PARTITION BY UPPER(TRIM(ticker))
            ORDER BY ingested_at DESC
        ) AS row_num

    FROM company_bronze

    WHERE ticker IS NOT NULL
)

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
FROM ranked_companies
WHERE row_num = 1;