CREATE OR REFRESH MATERIALIZED VIEW gold_table
COMMENT 'Stock price and volume trend analysis for the dashboard'
AS

WITH price_history AS (
    SELECT
        ticker,
        trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,

        LAG(close_price, 7) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
        ) AS close_7_days_ago,

        LAG(close_price, 30) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
        ) AS close_30_days_ago,

        LAG(close_price, 90) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
        ) AS close_90_days_ago,

        AVG(volume) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS avg_volume_7_days,

        AVG(volume) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS avg_volume_30_days,

        AVG(volume) OVER (
            PARTITION BY ticker
            ORDER BY trade_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS avg_volume_90_days

    FROM stock_silver
),

trends AS (
    SELECT
        *,

        ROUND(
            close_price - close_7_days_ago,
            2
        ) AS price_change_7_days,

        ROUND(
            close_price - close_30_days_ago,
            2
        ) AS price_change_30_days,

        ROUND(
            close_price - close_90_days_ago,
            2
        ) AS price_change_90_days,

        ROUND(
            100 * (close_price - close_7_days_ago)
            / NULLIF(close_7_days_ago, 0),
            2
        ) AS price_change_pct_7_days,

        ROUND(
            100 * (close_price - close_30_days_ago)
            / NULLIF(close_30_days_ago, 0),
            2
        ) AS price_change_pct_30_days,

        ROUND(
            100 * (close_price - close_90_days_ago)
            / NULLIF(close_90_days_ago, 0),
            2
        ) AS price_change_pct_90_days

    FROM price_history
)

SELECT
    trends.ticker,
    company.company_name,
    company.exchange,
    company.currency,
    company.country,
    company.sector,
    company.industry,
    company.market_capitalization,
    company.pe_ratio,
    company.dividend_yield,
    company.week_52_high,
    company.week_52_low,

    trends.trade_date,
    trends.open_price,
    trends.high_price,
    trends.low_price,
    trends.close_price,
    trends.volume,

    trends.price_change_7_days,
    trends.price_change_30_days,
    trends.price_change_90_days,

    trends.price_change_pct_7_days,
    trends.price_change_pct_30_days,
    trends.price_change_pct_90_days,

    ROUND(trends.avg_volume_7_days, 0)
        AS avg_volume_7_days,

    ROUND(trends.avg_volume_30_days, 0)
        AS avg_volume_30_days,

    ROUND(trends.avg_volume_90_days, 0)
        AS avg_volume_90_days

FROM trends

LEFT JOIN company_silver AS company
    ON trends.ticker = company.ticker;