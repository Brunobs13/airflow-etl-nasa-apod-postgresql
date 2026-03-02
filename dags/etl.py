"""Daily ETL DAG: NASA APOD API to PostgreSQL.

Flow:
1. Ensure destination table exists
2. Extract APOD payload from NASA API
3. Transform response to curated schema
4. Load curated record into PostgreSQL
"""

from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


DEFAULT_ARGS = {"owner": "data-platform", "retries": 2}


with DAG(
    dag_id="daily_nasa_apod_to_postgres",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "api", "postgres"],
) as dag:
    @task
    def create_table() -> None:
        postgres_hook = PostgresHook(postgres_conn_id="my_postgres_connection")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS apod_data (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            explanation TEXT,
            url TEXT,
            date DATE,
            media_type VARCHAR(50)
        );
        """
        postgres_hook.run(create_table_query)

    extract_apod = HttpOperator(
        task_id="extract_apod",
        http_conn_id="nasa_api",
        endpoint="planetary/apod",
        method="GET",
        data={"api_key": "{{ conn.nasa_api.extra_dejson.api_key }}"},
        response_filter=lambda response: response.json(),
        response_check=lambda response: response.status_code == 200,
    )

    @task
    def transform_apod_data(response: dict) -> dict:
        return {
            "title": response.get("title", ""),
            "explanation": response.get("explanation", ""),
            "url": response.get("url", ""),
            "date": response.get("date", ""),
            "media_type": response.get("media_type", ""),
        }

    @task
    def load_data_to_postgres(apod_data: dict) -> None:
        postgres_hook = PostgresHook(postgres_conn_id="my_postgres_connection")
        insert_query = """
        INSERT INTO apod_data (title, explanation, url, date, media_type)
        VALUES (%s, %s, %s, %s, %s);
        """
        postgres_hook.run(
            insert_query,
            parameters=(
                apod_data["title"],
                apod_data["explanation"],
                apod_data["url"],
                apod_data["date"],
                apod_data["media_type"],
            ),
        )

    create_task = create_table()
    transformed = transform_apod_data(extract_apod.output)
    load_task = load_data_to_postgres(transformed)

    create_task >> extract_apod >> transformed >> load_task
