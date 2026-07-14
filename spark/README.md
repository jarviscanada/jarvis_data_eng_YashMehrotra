# Apache Spark & Databricks Data Engineering

## Introduction

This repository contains a collection of Apache Spark and Databricks projects completed as part of the Jarvis Data Engineering training program. The projects cover core Spark concepts, distributed data processing, ETL pipeline development, Medallion Architecture, Delta Live Tables (DLT), and business intelligence reporting using Databricks.

---

# World Development Indicators (WDI)

The World Development Indicators notebook introduces Apache Spark DataFrame operations using economic data stored in Hive. The exercises contain Spark transformations, SQL queries, joins, aggregations, caching, and lazy evaluation while analyzing GDP growth across multiple countries.

Example analyses include:

- Historical GDP growth for Canada
- GDP growth comparisons across countries
- Maximum GDP growth recorded by each country
- Identification of the year corresponding to each country's highest GDP growth

---

# PySpark

This section contains a series of notebooks focused on ETL development and analytical processing using Spark DataFrames.

### ETL pgExercises CSV Files

Introduces the ETL process by importing relational datasets from CSV files into Spark. The notebook covers schema creation, managed tables, and data ingestion workflows.

### Spark DataFrame Manipulation

Explores the Spark DataFrame API and Spark SQL using the pgExercises dataset. The notebook covers filtering, joins, aggregations, window functions, and analytical queries involving bookings, facilities, and member activity.

### Spark ETL Jobs

Builds larger ETL workflows by integrating Spark with PostgreSQL databases, Parquet files, and REST APIs. The notebook demonstrates multi-source data ingestion, transformation, and storage using Spark.

---

# Azure Databricks Medallion ETL Pipeline

This project implements an end-to-end ETL pipeline in Azure Databricks using the Medallion Architecture. Multiple data sources are ingested using different Azure services before being transformed through the Bronze, Silver, and Gold layers to support fraud analytics and reporting.

## Architecture

The pipeline integrates Azure services with Databricks to ingest, transform, and analyze financial transaction data.

The ingestion workflow consists of:

- **Azure SQL Database**  Transaction and card data are loaded into Azure SQL Database and ingested into Databricks using JDBC and Lakeflow Connect.
- **Azure Data Lake Storage (ADLS)**  User data is uploaded to Azure Storage and accessed through Unity Catalog External Locations.
- **Azure Data Factory (ADF)**  Merchant category codes and fraud labels stored in Azure Blob Storage are copied into Databricks using Azure Data Factory.

After ingestion, the datasets are processed through the Medallion Architecture before being orchestrated using Databricks Workflows.

---

## Bronze

The Bronze layer stores raw data exactly as it is received from each source system. Separate Delta tables are created for transactions, cards, users, merchant categories, and fraud labels while preserving the original records for auditing and reprocessing.

---

## Silver

The Silver layer performs data cleansing and enrichment by:

- Standardizing schemas and data types
- Removing invalid and duplicate records
- Joining transaction data with card, user, merchant category, and fraud label datasets
- Creating curated datasets for downstream analytics

---

## Gold

The Gold layer creates business-ready tables that answer common fraud analytics questions, including:

- Fraud trends over time
- Fraud rate by merchant category
- Fraud distribution by day of the week
- High-risk users
- Suspicious transaction patterns
- Fraud losses by merchant and category
- Transaction behaviour before and after fraudulent activity

These Gold tables serve as the source for the Databricks dashboard.

---

## Dashboard

The dashboard is built directly from the Gold tables and provides interactive visualizations for fraud monitoring and business reporting.

<p align="center">
    <img src="images/Dashboard.png" width="900">
</p>

# Databricks Delta Live Tables (DLT)

This project implements a Delta Live Tables pipeline that processes historical stock market data obtained from the Alpha Vantage API. The pipeline follows the Medallion Architecture and produces curated analytical datasets for reporting and visualization.

## Pipeline

<p align="center">
    <img src="images/Pipeline.png" width="900">
</p>

### Data Ingestion

Historical stock prices and company information are retrieved from the Alpha Vantage REST API and loaded into Delta Lake for downstream processing.

### Bronze

The Bronze layer stores raw stock prices and company metadata as Delta Live Tables while preserving the original source data.

### Silver

The Silver layer removes duplicate records, validates data types, standardizes ticker symbols, and prepares clean datasets for analytical use.

### Gold

The Gold layer generates business-ready datasets containing:

- Daily stock prices
- Rolling price changes
- Trading volume metrics
- Company metadata
- Market capitalization
- Sector and industry information

## Dashboard

The Gold tables are visualized through an interactive Databricks dashboard.

<p align="center">
    <img src="images/Dashboard2.png" width="900">
</p>

# Technologies

- Apache Spark
- PySpark
- Spark SQL
- Databricks
- Azure Databricks
- Delta Lake
- Delta Live Tables (DLT)
- Python
- Hive
- JDBC
- Azure SQL Database
- Azure Data Factory
- Unity Catalog
- Lakeflow Connect
- Alpha Vantage API