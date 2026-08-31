# NYC Taxi ETL Data Pipeline — POC

A proof-of-concept (POC) ETL data pipeline for processing **New York City Taxi and Limousine Commission (TLC) Trip Record Data**.

This project demonstrates an end-to-end data pipeline including:

- source data quality checks
- data transformation
- report aggregation
- orchestration with Airflow
- containerized ETL and orchestration environments
- unit testing
- basic deployment preparation

> **POC disclaimer:** This project has not undergone QA. It is primarily a showcase of a working ETL pipeline. **The correctness of the generated results is not guaranteed.**

---

## Technology Stack

- **Python**
- **Polars** — data processing
- **pytest** — unit testing
- **Apache Airflow** — orchestration and scheduling
- **Docker** — containerization

### Data Source

New York City Taxi and Limousine Commission (TLC) Trip Record Data:

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

---

## Prerequisites

To run this project locally, install:

- [Docker](https://www.docker.com/get-started/)

---

# Architecture

The project separates **ETL code** from **orchestration code**.

The orchestration and ETL processes are defined in separate packages:

- **ETL code** — Python scripts responsible for data quality checks, transformations, and reporting
- **Airflow code** — DAGs responsible for orchestrating and scheduling the ETL operations

Both parts are separately containerized using Docker.

The exact Docker build and execution commands are described in the [Running](#running) section.

> In a production implementation, it would be good practice to separate the ETL code and orchestration code into different repositories. They are kept in a single repository here because the task requires a single repository containing both.

---

# Running

## 1. Build the ETL Docker image

From the project root:

```bash
docker build -t nyc-taxi-etl:latest .
```

## 2. Build the Airflow environment

From `root/airflow`:

```bash
docker compose build airflow
```

## 3. Start Airflow

From `root/airflow`:

```bash
docker compose up
```

## 4. Open the Airflow UI

Access the Airflow UI in a web browser:

```text
http://0.0.0.0:8080/
```

### Airflow credentials

Airflow credentials are generated dynamically.

The password for the `admin` user can be found in the Airflow logs.

Example:

```text
airflow-1  | Simple auth manager | Password for user 'admin': TmhM8przdKzsqwpA
```

---

## Running ETL Scripts Independently

After completing step 1, the Python ETL scripts can also be executed independently without Airflow.

For example:

### Taxi — data quality check

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  nyc-taxi-etl:latest \
  python src/etl/dq/report_taxi_green.py \
  --date=20260826 \
  --year=2026 \
  --month=1
```

### Taxi — processing

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  nyc-taxi-etl:latest \
  python src/etl/processing/process_taxi.py \
  --date=20260826 \
  --year=2026 \
  --month=1
```

### Reports — aggregation

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  nyc-taxi-etl:latest \
  python src/etl/reports/report.py \
  --date=20260826 \
  --year=2026 \
  --month=1
```

### Reports — read generated report

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  nyc-taxi-etl:latest \
  python src/etl/reports/report_read.py \
  --date=20260826
```

---


# ETL pipeline
1. **dq checks source data**
   - reading data from data/input location (lookup, taxi yellow, taxi green, rental)
   - checks performed on each source separately
   - results in log
2. **transforms source data**
   - reading data from data/input location (taxi yellow, taxi green, rental)
   - transform processes logically grouped (taxi/rental, lookup not needed to be processed)
   - results stored into data/output/transformed/trips location
   - tip: introduce partitioning also by trips
3. **aggregates transformed data into report**
   - reading data from /data/output/transformed/trips location (taxi/rental) and /data/input/taxi_zone_lookup.csv
   - results stored into data/output/report location
4. **reads report results**
   - reading data from /data/output/report location (taxi/rental) and /data/input/taxi_zone_lookup.csv


# Project Structure

The project contains both the ETL implementation and Airflow orchestration.

```text
.
├── airflow/
├── data/
├── src/
├── tests/
├── deploy/
└── .github/
```

## `airflow/`

Contains the Airflow orchestration environment:

- Docker files for building and running the Airflow environment
- DAG definitions

The main DAG is:

```text
airflow/dags/nyc_taxi_etl.py
```

The `nyc_taxi_etl.py` DAG defines the ETL pipeline with the following tasks:

1. **Print context attributes** — prints the input arguments as the starting point of the pipeline
2. **DQ tasks** — performs data quality checks for each data source
3. **Data source processing tasks** — transforms source data into clean data
4. **Report aggregation** — aggregates the transformed data into a report
5. **Report output** — prints the report generated by the previous task for a quick result overview

---

## `data/`

Location for all input and output files.

The directory is mounted into the Docker container as an external volume. This ensures that generated output is persisted even after the Docker container is terminated.

The required folder structure must be created in advance.

See [Data Structure](#data-structure) below.

---

## `src/`

Contains the ETL Python code.

### `src/etl/`

ETL operations are logically divided into the following packages:

#### `dq/` — Data Quality

Contains source data quality check reports.

Currently:

- DQ results are printed to the log
- Depending on the situation, `assert` operations could be used to stop further processing when serious issues are found — **not implemented**
- Depending on requirements, notifications could be triggered through email, Slack, Teams, etc. — **not implemented**

#### `processing/` — Data Processing

Contains scripts responsible for transforming source data into clean, valid data suitable for reporting.

#### `reports/` — Reporting

Contains report aggregation scripts based on the transformed data.

---

## `tests/`

Contains unit tests.

### `tests/unit/`

Contains unit tests for manual execution and/or CI/CD purposes.

---

More specifics are described in the following sections.

---

# Data Structure

The input/output directory structure is **static** and must be created in advance.

Polars fails when attempting to store data into a directory that does not exist.

Therefore, when processing a new month of source data, the required monthly/daily partitions must be created before reading and storing the data.

The expected structure is:

```text
data/
├── input/
│   ├── month=yyyymm/
│   │   └── *.parquet
│   └── taxi_zone_lookup.csv
│
└── output/
    ├── report/
    │   └── day=yyyymmdd/
    │       └── result.parquet
    │
    └── transformed/
        └── trips/
            ├── rental/
            │   └── day=yyyymmdd/
            │       └── transformed.parquet
            │
            └── taxi/
                └── day=yyyymmdd/
                    └── transformed.parquet
```
An example of required directory structure is provided in:

```text
data_structure.zip
```

### Input partitioning

Source data are partitioned by **year and month**, for example:

```text
202601
```

Project uses **daily partitioning for output data**.

Whether the final implementation should continue using daily output partitions or use monthly partitions instead is open for discussion. The choice depends on multiple aspects and expectations of the final implementation.

---

# Versioning

Project is version-controlled using GitHub.

GitHub Actions are configured to execute unit tests defined in:

```text
.github/workflows/tests.yml
```

---

# Unit Tests

Unit tests are defined in:

```text
tests/unit
```

They are executed automatically by GitHub Actions when changes are pushed or merged.

## Run tests locally

Install test dependencies from the project root:

```bash
python -m pip install -e ".[test]"
```

Then execute:

```bash
python -m pytest
```

---

# Scheduling

ETL pipeline is scheduled through Airflow DAG.

The schedule is defined as:

```python
schedule="0 1 1 * *"
```

This means:

> **Every first day of the month at 01:00 AM**

Airflow environment is expected to be running for scheduled execution to take place.

DAG can also be triggered manually from the Airflow UI.

---

## DAG Input Parameters

The DAG expects three values:

### Processing date

Used mainly to store processed/aggregated data into the appropriate **daily partition**.

### Source data month

Used to identify the source data partition to process.

### Source data year

Used to identify the source data partition to process.

In other words:

```text
processing date → output daily partition
source month    → input data partition
source year     → input data partition
```

---

# Deployment — DRAFT

Considered target deployment environment is **AWS**.

Deployment steps are currently provided as draft scripts in:

```text
./deploy
```

Available scripts are:

### Airflow deployment

Copy/sync Airflow code to AWS S3:

```text
deploy/deploy_airflow_s3.sh
```

### Configuration deployment

Deploy configuration files to AWS S3:

```text
deploy/deploy_configs_s3.sh
```

### ETL deployment

Copy/sync ETL code to AWS S3:

```text
deploy/deploy_etl_s3.sh
```

### Docker image deployment

Docker images can be pushed to container registries.

#### Google Container Registry (GCR)

Build/push image using:

```text
deploy/docker_push_gcr.sh
```

#### AWS Elastic Container Registry (ECR)

Read the image from GCR and push it to AWS ECR using:

```text
deploy/docker_push_ecr.sh
```

---

## Project Deployment Options

ETL code can be deployed in either of two ways:

1. Copy the project structure into an S3 bucket
2. Build the ETL code into a Docker image and push the image to a remote Docker registry

The deployment scripts are prepared so they can also be used within a CI/CD pipeline as part of a deployment stage.

---

# Data Limit

To make it possible to run the project locally with limited resources, a record limit is applied when reading the input data.

The current limit is:

```text
50,000 records
```

The value is defined as the `DATA_RECORDS_LIMIT` constant in:

```text
src/etl/__init__.py
```

For higher data volumes, the solution is expected to be deployed into an environment with sufficient resources.

---

# Summary

This project is a **proof-of-concept implementation of an end-to-end NYC TLC data pipeline**.

It demonstrates:

- Dockerized ETL processing
- Dockerized Airflow orchestration
- Source data quality checks
- Data transformation
- Report aggregation
- Persistent input/output data
- Daily output partitioning
- Automated unit testing
- Monthly Airflow scheduling
- Manual Airflow execution
- Draft AWS deployment options
- CI/CD-ready deployment scripts

The implementation is intentionally a POC and has **not been QA-validated**. Consequently, the generated ETL and reporting results should not be considered production-grade or guaranteed to be correct.
