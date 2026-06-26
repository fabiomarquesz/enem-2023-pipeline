"""
ENEM 2023 Pipeline — Bronze Ingestion from S3
Baixa o ZIP do S3, extrai e ingere no RDS PostgreSQL
"""

import os
import io
import zipfile
import boto3
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from tqdm import tqdm
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)
load_dotenv()

# Config S3
S3_BUCKET  = "enem-pipeline-fabiomarques"
S3_KEY     = "bronze/microdados_enem_2023.zip"
CHUNK_SIZE = 10_000
ENCODING   = "latin-1"

# Config RDS
DB_CONFIG = {
    "host":     "enem-pipeline-db.c8dumieki7rc.us-east-1.rds.amazonaws.com",
    "port":     5432,
    "dbname":   "enem_db",
    "user":     "enem_user",
    "password": os.getenv("RDS_PASSWORD", "EnemPipeline2024!"),
    "sslmode":  "require",
}

COLUMNS = [
    "NU_INSCRICAO", "NU_ANO", "TP_FAIXA_ETARIA", "TP_SEXO",
    "TP_ESTADO_CIVIL", "TP_COR_RACA", "TP_NACIONALIDADE",
    "TP_ST_CONCLUSAO", "TP_ANO_CONCLUIU", "TP_ESCOLA", "TP_ENSINO",
    "IN_TREINEIRO", "CO_MUNICIPIO_ESC", "NO_MUNICIPIO_ESC",
    "CO_UF_ESC", "SG_UF_ESC", "TP_DEPENDENCIA_ADM_ESC",
    "TP_LOCALIZACAO_ESC", "TP_SIT_FUNC_ESC", "CO_MUNICIPIO_PROVA",
    "NO_MUNICIPIO_PROVA", "CO_UF_PROVA", "SG_UF_PROVA",
    "NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT",
    "NU_NOTA_REDACAO", "TP_PRESENCA_CN", "TP_PRESENCA_CH",
    "TP_PRESENCA_LC", "TP_PRESENCA_MT", "TP_LINGUA",
    "TP_STATUS_REDACAO", "Q001", "Q002", "Q003", "Q004", "Q005", "Q006"
]

def download_from_s3() -> bytes:
    log.info(f"Baixando s3://{S3_BUCKET}/{S3_KEY}...")
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
    data = obj["Body"].read()
    log.info(f"Download concluído: {len(data)/1024/1024:.1f} MB")
    return data

def find_csv_in_zip(zip_bytes: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        csvs = [f for f in z.namelist()
                if f.endswith(".csv") and "MICRODADOS" in f.upper()]
        if not csvs:
            raise FileNotFoundError("CSV não encontrado no ZIP")
        log.info(f"CSV encontrado: {csvs[0]}")
        return csvs[0]

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def insert_batch(conn, batch: pd.DataFrame):
    batch.columns = [c.lower() for c in batch.columns]
    cols = [c.lower() for c in COLUMNS]
    rows = [
        tuple(row[c] if c in row.index and pd.notna(row[c]) else None for c in cols)
        for _, row in batch.iterrows()
    ]
    sql = f"""
        INSERT INTO bronze.enem_2023 ({', '.join(cols)})
        VALUES %s
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=1000)
    conn.commit()

def main():
    log.info("=== Ingestão Bronze S3 → RDS — ENEM 2023 ===")

    # Download do S3
    zip_bytes = download_from_s3()
    csv_name  = find_csv_in_zip(zip_bytes)

    # Conecta ao RDS
    conn = get_connection()
    log.info("Conectado ao RDS PostgreSQL")

    # Trunca tabela
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE bronze.enem_2023 RESTART IDENTITY;")
    conn.commit()

    # Ingere em chunks
    total = 0
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        with z.open(csv_name) as csv_file:
            chunks = pd.read_csv(
                csv_file,
                sep=";",
                encoding=ENCODING,
                usecols=COLUMNS,
                dtype=str,
                chunksize=CHUNK_SIZE
            )
            for i, chunk in enumerate(tqdm(chunks, desc="Ingerindo")):
                insert_batch(conn, chunk)
                total += len(chunk)
                if (i + 1) % 50 == 0:
                    log.info(f"{total:,} linhas inseridas...")

    conn.close()
    log.info(f"=== Concluído: {total:,} linhas no RDS ===")

if __name__ == "__main__":
    main()
