FROM apache/airflow:2.9.1

USER airflow
RUN pip install --no-cache-dir \
    pandas \
    psycopg2-binary \
    python-dotenv \
    tqdm \
    requests \
    boto3 \
    dbt-postgres
