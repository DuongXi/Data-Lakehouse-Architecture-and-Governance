# Big Data Lakehouse Pipeline

## Overview
This repository implements an Olist-style Lakehouse pipeline using Apache Spark, Iceberg, Airflow DAGs, Streamlit dashboarding, and test automation.

The architecture follows a medallion-style Bronze → Silver → Gold flow with:
- Bronze: raw parquet data in S3
- Silver: cleaned Silver tables written as Iceberg managed tables
- Gold: dimension and fact tables in a star schema for analytics

More detail at: [Report.pdf](https://github.com/DuongXi/Data-Lakehouse-Architecture-and-Governance/blob/main/Report.pdf)

## Repository Structure
- `dags/`
  - `dag_raw2bronze.py`: raw CSV to Bronze parquet conversion.
  - `dag_bronze2silver.py`: Bronze parquet data cleanup and Silver Iceberg table creation.
  - `dag_silver2gold.py`: Silver Iceberg tables to Gold dimension and fact tables.
- `dashboard/`
  - `connect_db.py`: create local sample Parquet and upload to S3/MinIO.
  - `spark_s3.py`: Spark sample read/filter/write flow over `s3a://`.
  - `dashboard.py`: Streamlit dashboard for pipeline metrics logs.
  - `convert_to_csv.py`: helper to export Parquet data to CSV.
  - `olist_data_pipeline.py`: pipeline helper utilities for CSV-to-Parquet ingestion.
- `data_processing/`
  - `ingest_to_raw.py`, `raw_to_clean.py`, `clean_to_curated.py`, `ultility.py`: supporting pipeline utilities for ingestion and transformation.
- `monitoring/`
  - `docker-compose.yml`: Grafana + PostgreSQL monitoring stack.
- `test/`
  - `acid_test.py`, `performance_test.py`: ACID and performance validation tests.

## Data Flow
1. `dags/dag_raw2bronze.py`
   - Reads source CSV data from an S3 path.
   - Writes Bronze parquet files to `s3a://<bucket>/bronze/<table>/`.

2. `dags/dag_bronze2silver.py`
   - Reads Bronze parquet files from S3.
   - Cleans and validates customers, orders, products, sellers, order_items, order_reviews, order_payments, and geolocation.
   - Writes Silver tables to Iceberg using `saveAsTable` into `olist.silver.*`.

3. `dags/dag_silver2gold.py`
   - Reads Silver Iceberg tables.
   - Builds Gold dimensions: `dim_customers`, `dim_products`, `dim_sellers`, `dim_date`.
   - Builds Gold facts: `fact_sales`, `fact_reviews`, `fact_shipping`.
   - Writes Gold tables as Iceberg managed tables in `olist.gold.*`.

## Key Data Model
The Gold layer produces a star schema with:
- Dimensions: `dim_customers`, `dim_products`, `dim_sellers`, `dim_date`
- Facts: `fact_sales`, `fact_reviews`, `fact_shipping`

The Silver layer includes cleaned reference tables for:
- `customers`, `orders`, `products`, `sellers`, `order_items`, `order_payments`, `order_reviews`, `geolocation`

## Requirements
Install the required Python packages from `requirements.txt`:
- `boto3`
- `pandas`
- `pyarrow`
- `fastparquet`
- `pyspark`
- `streamlit`
- `plotly`
- `psycopg2-binary`
- `apache-airflow`

Additional requirements:
- Java / OpenJDK 17 for PySpark
- S3-compatible storage or MinIO for test deployment
- Docker

## Configuration
### S3
The DAGs use `olist_guest.json` for bucket configuration and expect S3-compatible access via Spark `s3a://`.

### Environment variables
Some helper scripts use environment variables stored in `.env` for AWS/S3 credentials:
- `ACCESS_KEY`
- `SECRET_KEY`

For Spark, also set `JAVA_HOME` to the Java installation path.

## How to Run
### 1. Upload sample data
Use `dashboard/connect_db.py` to create a sample Parquet file and upload it to S3/MinIO.

### 2. Run Bronze ingestion
Execute `dags/dag_raw2bronze.py` or trigger the Airflow DAG `raw_to_bronze_pipeline`.

### 3. Run Bronze → Silver transformation
Execute `dags/dag_bronze2silver.py` or trigger the Airflow DAG `bronze_to_silver_pipeline`.

### 4. Run Silver → Gold transformation
Execute `dags/dag_silver2gold.py` or trigger the Airflow DAG `silver_to_gold_pipeline`.

### 5. View the dashboard
Run `dashboard/dashboard.py` with Streamlit:
```bash
streamlit run dashboard/dashboard.py
```
This dashboard reads pipeline metric logs and displays throughput, execution time, and raw log history.

## Testing
Run the repository tests from `test/`:
```bash
python test/acid_test.py
python test/performance_test.py
```

## Monitoring
Start the Grafana/PostgreSQL stack in `monitoring/`:
```bash
docker compose -f monitoring/docker-compose.yml up -d
```
