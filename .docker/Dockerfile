FROM apache/airflow:2.9.1

# Instala dependências do projeto como usuário airflow
USER airflow
RUN pip install --no-cache-dir \
    pandas \
    psycopg2-binary \
    python-dotenv \
    tqdm \
    requests
