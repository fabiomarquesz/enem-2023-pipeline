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
