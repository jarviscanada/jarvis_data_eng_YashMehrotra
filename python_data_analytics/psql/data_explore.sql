-- Inspect the table schema
\d+ retail;

-- Show first 10 rows
SELECT 
  * 
FROM 
  retail 
LIMIT 
  10;

-- Check # of records
SELECT 
  Count(*) 
FROM 
  retail;

-- Number of clients
select 
  count(distinct customer_id) 
from 
  retail;

-- Invoice date range
select 
  max(invoice_date) as max, 
  min(invoice_date) as min 
from 
  retail;

-- Number of SKU merchants
select 
  count(distinct stock_code) 
from 
  retail;

-- Calculate average invoice amount excluding invoices with a negative amount
select 
  avg(invoice_total) 
from 
  (
    select 
      invoice_no, 
      sum(unit_price * quantity) as invoice_total 
    from 
      retail 
    group by 
      invoice_no 
    having 
      sum(unit_price * quantity) > 0
  ) as positive_invoices;

-- Calculate total revenue
select 
  sum(unit_price * quantity) 
from 
  retail;

-- Calculate total revenue by YYYYMM
select 
  cast(
    extract(
      year 
      from 
        invoice_date
    ) * 100 + extract(
      month 
      from 
        invoice_date
    ) as int
  ) as yyyymm, 
  sum(unit_price * quantity) as sum 
from 
  retail 
group by 
  yyyymm 
order by 
  yyyymm;

