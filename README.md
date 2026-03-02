# Airflow ETL Pipeline: NASA APOD to PostgreSQL

Production-style Airflow project that ingests NASA APOD data daily and stores curated records in PostgreSQL.

## Project Overview

This repository implements a complete ETL orchestration pattern using Apache Airflow, HTTP ingestion, transformation tasks, and PostgreSQL loading.

## Business Problem

Data teams need repeatable pipelines that can ingest external API data and persist it reliably for downstream analytics. This project provides a clean baseline for that workflow.

## Pipeline Architecture

1. `create_table` task ensures destination table exists.
2. `extract_apod` retrieves daily APOD payload from NASA API.
3. `transform_apod_data` shapes the raw response.
4. `load_data_to_postgres` inserts curated records in PostgreSQL.

## Tech Stack

- Apache Airflow (Astro Runtime)
- Python 3.11+
- `apache-airflow-providers-http`
- `apache-airflow-providers-postgres`
- PostgreSQL 13 (Docker Compose)

## Repository Structure

```text
.
├── dags/
│   └── etl.py
├── tests/dags/
├── docker-compose.yml
├── airflow_settings.yaml
├── requirements.txt
├── .env.example
└── README.md
```

## Local Setup

1. Start PostgreSQL for local testing:

```bash
docker compose up -d
```

2. Configure environment file:

```bash
cp .env.example .env
# update values as needed
```

3. Start Airflow locally:

```bash
astro dev start
```

4. Open Airflow UI at `http://localhost:8080`.
5. Trigger DAG `daily_nasa_apod_to_postgres`.

## Testing

Run DAG integrity tests:

```bash
astro dev pytest tests
```

## Security Notes

- API keys are pulled from Airflow Connections, not hardcoded in DAG code.
- `.env` and local runtime artifacts are excluded from version control.
- Database credentials are environment-driven in `docker-compose.yml`.

## Future Improvements

1. Add upsert/deduplication strategy by APOD date.
2. Add data quality checks (nulls, schema validation).
3. Add CI workflow for DAG import and lint checks.
4. Add alerting callbacks for failed runs.
