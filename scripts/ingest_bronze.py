# ENEM 2023 Pipeline - Bronze Ingestion 

import os
import zipfile
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from tqdm import tqdm
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

log = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do arquivo
ZIP_PATH = "data/bronze/microdados_enem_2023.zip"
CHUNK_SIZE = 10_000  # Número de linhas por chunk para leitura e inserção
ENCODING = "latin1"  # Codificação dos arquivos CSV do ENEM

# Configurações do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "enem_db"),
    "user": os.getenv("POSTGRES_USER", "enem_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "enem_pass")
}

# Colunas a serem importadas
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

def find_csv_in_zip(zip_path: str) -> str:
    """Encontra o arquivo CSV dentro do arquivo ZIP."""
    with zipfile.ZipFile(zip_path, 'r') as z:
        csvs = [f for f in z.namelist() if f.endswith('.csv') and "MICRODADOS" in f.upper()]
        if not csvs:
            raise FileNotFoundError("Nenhum arquivo CSV encontrado no ZIP.")
        log.info(f"CSV encontrado: {csvs[0]}")
        return csvs[0]
    
def get_connection():
    """Estabelece conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        log.info("Conexão com o banco de dados estabelecida.")
        return conn
    except Exception as e:
        log.error(f"Erro ao conectar ao banco de dados: {e}")
        raise

def truncate_table(conn):
    """Limpa a tabela de destino antes de inserir novos dados."""
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE bronze.enem_2023 RESTART IDENTITY;")
            conn.commit()
            log.info("Tabela bronze.enem_2023 truncada.")
    except Exception as e:
        log.error(f"Erro ao truncar a tabela: {e}")
        raise

def insert_batch(conn, batch: pd.DataFrame):
    """Insere um batch de linhas na tabela bronze."""
    # Normaliza nomes de colunas para lowercase
    batch.columns = [col.lower() for col in batch.columns]
    
    cols = [col.lower() for col in COLUMNS]
    rows = [tuple(row[c] if pd.notna(row[c]) else None for c in cols) 
            for _, row in batch.iterrows()]
    sql = f"""
        INSERT INTO bronze.enem_2023 (
            {', '.join(cols)}
        ) VALUES %s
    """
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows, page_size=1000)
            conn.commit()
    except Exception as e:
        log.error(f"Erro ao inserir batch: {e}")
        raise

def main():
    log.info("Iniciando processo de ingestão Bronze para ENEM 2023.")

    # Localização do arquivo ZIP
    csv_name = find_csv_in_zip(ZIP_PATH)

    # Estabelece conexão com o banco de dados
    conn = get_connection()
    log.info("Conexão com o PostgreSQL estabelecida.")

    # Limpa a tabela
    truncate_table(conn)

    # Lê o CSV em chunks e insere no banco
    total_rows = 0
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        with z.open(csv_name) as csv_file:
            chunks = pd.read_csv(
                csv_file, 
                sep=';', 
                encoding=ENCODING, 
                usecols=COLUMNS,
                dtype=str,  # Lê todas as colunas como string para evitar problemas de tipo 
                chunksize=CHUNK_SIZE
            )
            for i, chunk in enumerate(tqdm(chunks, desc="Ingerindo chunks")):
                insert_batch(conn, chunk)
                total_rows += len(chunk)
                if (i + 1) % 10 == 0:
                    log.info(f"{total_rows:,} linhas inseridas até agora...")

    conn.close()    
    log.info(f"Ingestão concluída. Total de linhas inseridas: {total_rows:,}")

if __name__ == "__main__":
    main()