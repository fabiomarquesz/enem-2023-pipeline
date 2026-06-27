# ENEM 2023 Data Pipeline

Pipeline de engenharia de dados end-to-end para os microdados do ENEM 2023 (INEP), seguindo a Medallion Architecture.

## Arquitetura
Bronze → Silver → Gold

- **Bronze:** 3.933.955 linhas ingeridas do CSV oficial do INEP
- **Silver:** dados limpos, tipados e validados (0 erros de transformação)
- **Gold:** KPIs analíticos agregados por UF, faixa etária e tipo de escola

## Stack

| Ferramenta | Versão | Função |
|---|---|---|
| Python | 3.12 | Ingestão e transformação |
| PostgreSQL | 16 | Armazenamento |
| Apache Airflow | 2.9.1 | Orquestração |
| Docker Compose | v5.1.4 | Infraestrutura |

## Estrutura
enem-2023-pipeline/

├── dags/                  # DAGs do Airflow

│   └── enem_pipeline_dag.py

├── scripts/               # Scripts de ingestão e transformação

│   ├── ingest_bronze.py

│   ├── transform_silver.py

│   └── build_gold.py

├── sql/                   # DDL das tabelas

│   ├── init.sql

│   ├── create_silver.sql

│   └── create_gold.sql

├── docker-compose.yml

└── README.md

## Principais KPIs gerados

- Média de notas por UF (matemática, redação, geral)
- Desempenho por tipo de escola (pública vs privada)
- Distribuição de notas de redação
- Desempenho por faixa etária

## Como executar

```bash
# 1. Sobe a stack
docker compose up -d

# 2. Baixa os microdados do INEP e coloca em data/bronze/

# 3. Roda o pipeline
python scripts/ingest_bronze.py
python scripts/transform_silver.py
python scripts/build_gold.py

# Ou acessa o Airflow em http://localhost:8080
# e dispara a DAG enem_2023_pipeline manualmente
```

## Autor

Fabio Marques — [@fabiomarquesz](https://github.com/fabiomarquesz)

## Arquitetura Cloud (Sprint 2)

Pipeline migrado para AWS:

| Componente | Local | Cloud |
|---|---|---|
| Storage | `data/bronze/` (disco) | AWS S3 |
| Banco de dados | PostgreSQL (Docker) | AWS RDS PostgreSQL |
| Credenciais | `.env` local | IAM + AWS CLI |

### Infraestrutura AWS

- **S3 Bucket:** `enem-pipeline-fabiomarques`
- **RDS:** `enem-pipeline-db` (PostgreSQL 16, db.t3.micro)
- **Região:** `us-east-1`

### Fluxo cloud
S3 (bronze/microdados_enem_2023.zip)

↓ boto3 download

RAM (streaming em chunks de 10k linhas)

↓ psycopg2 + SSL

RDS PostgreSQL (bronze.enem_2023 → 3.933.955 linhas)

## Configuração do dbt

O dbt usa um arquivo de conexão local em `~/.dbt/profiles.yml` — **nunca versionado no Git** por conter credenciais.

Crie o arquivo com a seguinte estrutura:

```yaml
enem_dbt:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5435
      user: enem_user
      password: <sua_senha>
      dbname: enem_db
      schema: silver
      threads: 4

    cloud:
      type: postgres
      host: <seu_endpoint_rds>.rds.amazonaws.com
      port: 5432
      user: enem_user
      password: <sua_senha>
      dbname: enem_db
      schema: silver
      threads: 4
      sslmode: require
```

Para rodar os modelos:
- Local: `cd enem_dbt && dbt run`
- Cloud: `cd enem_dbt && dbt run --target cloud`

