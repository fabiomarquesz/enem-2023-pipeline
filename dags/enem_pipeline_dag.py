"""
DAG: enem_2023_pipeline
Orquestra o pipeline completo: Bronze → Silver → Gold
Schedule: manual (on-demand) — pode ser alterado para @daily, @weekly etc.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import subprocess
import logging

log = logging.getLogger(__name__)

PROJ_DIR = "/opt/airflow/dags"

DEFAULT_ARGS = {
    "owner":            "fabio.marques",
    "depends_on_past":  False,
    "email_on_failure": False,
    "email_on_retry":   False,
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
}

def run_script(script_name: str):
    """Executa um script Python do projeto dentro do container."""
    result = subprocess.run(
        ["python", f"{PROJ_DIR}/scripts/{script_name}"],
        capture_output=True,
        text=True
    )
    if result.stdout:
        log.info(result.stdout)
    if result.stderr:
        log.warning(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(
            f"Script {script_name} falhou com código {result.returncode}"
        )
    log.info(f"Script {script_name} concluído com sucesso.")

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

    ingesta_bronze = PythonOperator(
        task_id="ingesta_bronze",
        python_callable=run_script,
        op_kwargs={"script_name": "ingest_bronze.py"},
    )

    transforma_silver = PythonOperator(
        task_id="transforma_silver",
        python_callable=run_script,
        op_kwargs={"script_name": "transform_silver.py"},
    )

    build_gold = PythonOperator(
        task_id="build_gold",
        python_callable=run_script,
        op_kwargs={"script_name": "build_gold.py"},
    )

    fim = BashOperator(
        task_id="fim",
        bash_command='echo "Pipeline ENEM 2023 concluído — $(date)"',
    )

    # Define a ordem de execução
    inicio >> ingesta_bronze >> transforma_silver >> build_gold >> fim

