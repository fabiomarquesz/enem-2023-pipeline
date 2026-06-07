# Silver Transformation - Lê da bronze, limpa e grava na Silver

import os
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

load_dotenv()
CHUNK_SIZE = 10_000

DB_CONFIG = {
    "host": "localhost",
    "port": os.getenv("POSTGRES_PORT", "5435"),
    "dbname": os.getenv("POSTGRES_DB", "enem_db"),
    "user": os.getenv("POSTGRES_USER", "enem_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "enem_pass"),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def to_int(val):
    # Converte para inteiro, retorna None se invalido
    try:
        v = str(val).strip().replace(',', '.')
        return int(float(v)) if v not in ('', 'nan', 'NaN', 'None') else None
    except (ValueError, TypeError):
        return None
    
def to_float(val):
    # Converte para float, retorna None se invalido
    try:
        v = str(val).strip().replace(',', '.')
        return float(v) if v not in ('', 'nan', 'NaN', 'None') else None
    except (ValueError, TypeError):
        return None

def to_char(val, size=1):
    # Limpa e retorna string de tamanho fixo, ou None se invalida
    try:
        v = str(val).strip()
        return v[:size] if v not in ('', 'nan', 'NaN', 'None') else None
    except (ValueError, TypeError):
        return None

def transform_chunk(df: pd.DataFrame) -> list:
    # Transforma um chunk Bronze em lista de tuplas Silver.
    rows = []
    for _, r in df.iterrows():
        rows.append((
            to_int(r['nu_inscricao']),
            to_int(r['nu_ano']),
            to_int(r['tp_faixa_etaria']),
            to_char(r['tp_sexo']),
            to_char(r['tp_estado_civil']),
            to_char(r['tp_cor_raca']),
            to_char(r['tp_nacionalidade']),
            to_char(r['tp_st_conclusao']),
            to_char(r['tp_ano_concluiu']),
            to_char(r['tp_escola']),
            to_char(r['tp_ensino']),
            to_char(r['in_treineiro']),
            to_int(r.get('co_municipio_esc')),
            to_char(r.get('no_municipio_esc'), 100),
            to_int(r.get('co_uf_esc')),
            to_char(r.get('sg_uf_esc'), 2),
            to_int(r.get('tp_dependencia_adm_esc')),
            to_int(r.get('tp_localizacao_esc')),
            to_int(r.get('tp_sit_func_esc')),
            to_int(r.get('co_municipio_prova')),
            to_char(r.get('no_municipio_prova'), 100),
            to_int(r.get('co_uf_prova')),
            to_char(r.get('sg_uf_prova'), 2),
            to_float(r.get('nu_nota_cn')),
            to_float(r.get('nu_nota_ch')),
            to_float(r.get('nu_nota_lc')),
            to_float(r.get('nu_nota_mt')),
            to_float(r.get('nu_nota_redacao')),
            to_int(r.get('tp_presenca_cn')),
            to_int(r.get('tp_presenca_ch')),
            to_int(r.get('tp_presenca_lc')),
            to_int(r.get('tp_presenca_mt')),
            to_int(r.get('tp_lingua')),
            to_int(r.get('tp_status_redacao')),
            to_char(r.get('q001')),
            to_char(r.get('q002')),
            to_char(r.get('q003')),
            to_char(r.get('q004')),
            to_char(r.get('q005')),
            to_char(r.get('q006')),
            to_int(r.get('id')),
        ))
    return rows

INSERT_SQL = """
    INSERT INTO silver.enem_2023 (
        nu_inscricao, nu_ano, tp_faixa_etaria, tp_sexo,
        tp_estado_civil, tp_cor_raca, tp_nacionalidade,
        tp_st_conclusao, tp_ano_concluiu, tp_escola, tp_ensino,
        in_treineiro, co_municipio_esc, no_municipio_esc,
        co_uf_esc, sg_uf_esc, tp_dependencia_adm_esc,
        tp_localizacao_esc, tp_sit_func_esc, co_municipio_prova,
        no_municipio_prova, co_uf_prova, sg_uf_prova,
        nu_nota_cn, nu_nota_ch, nu_nota_lc, nu_nota_mt,
        nu_nota_redacao, tp_presenca_cn, tp_presenca_ch,
        tp_presenca_lc, tp_presenca_mt, tp_lingua,
        tp_status_redacao, q001, q002, q003, q004, q005, q006,
        bronze_id
    ) VALUES %s
"""

def main():
    log.info("Iniciando transformação Silver...")

    conn = get_connection()

    # Limpa Silver antes de reprocessar
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE silver.enem_2023 RESTART IDENTITY;")
    conn.commit()
    log.info("Tabela silver.enem_2023 truncada.")

    # Conta total para o tdqdm
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM bronze.enem_2023;")
        total = cur.fetchone()[0]
    log.info(f"Total de registros Bronze: {total:,}")

    total_ok = 0
    total_erros = 0
    offset = 0

    with tqdm(total=total, desc="Transformando") as pbar:
        while offset < total:
            # Lê chunk da Bronze
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM bronze.enem_2023 ORDER BY id LIMIT %s OFFSET %s",
                    (CHUNK_SIZE, offset)
                )
                cols = [d[0] for d in cur.description]
                rows_raw = cur.fetchall()

            if not rows_raw:
                break

            df = pd.DataFrame(rows_raw, columns=cols)

            try:
                rows_transformed = transform_chunk(df)
                with conn.cursor() as cur:
                    execute_values(cur, INSERT_SQL, rows_transformed, page_size=1000)
                conn.commit()
                total_ok += len(rows_transformed)
            except Exception as e:
                log.error(f"Erro no chunk offset {offset}: {e}")
                conn.rollback()
                total_erros += len(df)

            offset += CHUNK_SIZE
            pbar.update(len(rows_raw))

    conn.close()
    log.info(f"=== Silver concluída: {total_ok:,} OK | {total_erros:,} erros ===")

if __name__ == "__main__":
    main()