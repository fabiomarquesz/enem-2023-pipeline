"""
DAG: enem_cloud_pipeline
Orquestra o pipeline cloud: S3 → RDS Bronze → dbt Silver → dbt Gold
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner":            "fabio.marques",
    "depends_on_past":  False,
    "email_on_failure": False,
    "email_on_retry":   False,
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
}

# Caminhos dentro do container Airflow
SCRIPTS_DIR = "/opt/airflow/dags/scripts"
DBT_DIR     = "/opt/airflow/dags/enem_dbt"
PYTHON      = "python"
DBT         = "dbt"

with DAG(
    dag_id="enem_cloud_pipeline",
    description="Pipeline cloud ENEM 2023: S3 → RDS → dbt Silver → dbt Gold",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["enem", "cloud", "s3", "rds", "dbt"],
) as dag:

    inicio = BashOperator(
        task_id="inicio",
        bash_command='echo "Iniciando pipeline cloud ENEM 2023 — $(date)"',
    )

    ingesta_bronze_s3 = BashOperator(
        task_id="ingesta_bronze_s3",
        bash_command=f"cd {SCRIPTS_DIR} && {PYTHON} ingest_bronze_s3.py",
        execution_timeout=timedelta(minutes=60),
    )

    dbt_silver = BashOperator(
        task_id="dbt_silver",
        bash_command=f"cd {DBT_DIR} && {DBT} run --target cloud --select staging silver --profiles-dir {DBT_DIR}",
        execution_timeout=timedelta(minutes=30),
    )

    dbt_gold = BashOperator(
        task_id="dbt_gold",
        bash_command=f"cd {DBT_DIR} && {DBT} run --target cloud --select gold --profiles-dir {DBT_DIR}",
        execution_timeout=timedelta(minutes=15),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && {DBT} test --target cloud --select silver --profiles-dir {DBT_DIR}",
        execution_timeout=timedelta(minutes=10),
    )

    fim = BashOperator(
        task_id="fim",
        bash_command='echo "Pipeline cloud ENEM 2023 concluído — $(date)"',
    )

    inicio >> ingesta_bronze_s3 >> dbt_silver >> dbt_gold >> dbt_test >> fim

