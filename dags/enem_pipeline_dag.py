"""
DAG: enem_2023_pipeline
Orquestra o pipeline: Bronze → Silver → Gold
Usa BashOperator para maior estabilidade em processos longos
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
    "retry_delay":      timedelta(minutes=2),
    "execution_timeout": timedelta(minutes=60),
}

SCRIPTS_DIR = "/opt/airflow/dags/scripts"
PYTHON      = "python"

with DAG(
    dag_id="enem_2023_pipeline",
    description="Pipeline ENEM 2023: Bronze → Silver → Gold",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["enem", "educacao", "pipeline"],
) as dag:

    inicio = BashOperator(
        task_id="inicio",
        bash_command='echo "Iniciando pipeline ENEM 2023 — $(date)"',
    )

    ingesta_bronze = BashOperator(
        task_id="ingesta_bronze",
        bash_command=f"cd {SCRIPTS_DIR} && {PYTHON} ingest_bronze.py",
        execution_timeout=timedelta(minutes=45),
    )

    transforma_silver = BashOperator(
        task_id="transforma_silver",
        bash_command=f"cd {SCRIPTS_DIR} && {PYTHON} transform_silver.py",
        execution_timeout=timedelta(minutes=30),
    )

    build_gold = BashOperator(
        task_id="build_gold",
        bash_command=f"cd {SCRIPTS_DIR} && {PYTHON} build_gold.py",
        execution_timeout=timedelta(minutes=10),
    )

    fim = BashOperator(
        task_id="fim",
        bash_command='echo "Pipeline ENEM 2023 concluído — $(date)"',
    )

    inicio >> ingesta_bronze >> transforma_silver >> build_gold >> fim
