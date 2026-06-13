"""
ENEM 2023 Pipeline - Gold Layer
Calcula KPIs analíticos a partir da Silver e popula as tabelas Gold. """

import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

log = logging.getLogger(__name__)
load_dotenv()

DB_CONFIG = {
    'host': "localhost",
    'port': os.getenv('POSTGRES_PORT', '5435'),
    'dbname': os.getenv('POSTGRES_DB', 'enem_db'),
    'user': os.getenv('POSTGRES_USER', 'enem_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'enem_pass'),
}

FAIXA_ETARIA = {
    1: "Menor de 17 anos", 2: "17 anos", 3: "18 anos", 
    4: "19 anos", 5: "20 anos", 6: "21 anos", 
    7: "22 anos", 8: "23 anos", 9: "24 anos", 
    10: "25 anos ou mais", 11: "Entre 26 e 30 anos",
    12: "Entre 31 e 35 anos", 13: "Entre 36 e 40 anos", 
    14: "Entre 41 e 45 anos", 15: "Entre 46 e 50 anos", 
    16: "Entre 51 e 55 anos", 17: "Entre 56 e 60 anos", 
    18: "Entre 61 e 65 anos", 19: "Entre 66 e 70 anos", 
    20: "Maior de 70 anos",
}

TIPO_ESCOLA = {
    1: "Não respondeu", 
    2: "Pública", 
    3: "Privada", 
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def build_desempenho_por_uf(conn):
    log.info("Calculando desempenho médio por UF...")
    sql_read = """
        SELECT
            sg_uf_prova                             AS sg_uf,
            COUNT(*)                                AS total_participantes,
            ROUND(AVG(nu_nota_mt)::numeric, 2)      AS media_matematica,
            ROUND(AVG(nu_nota_cn)::numeric, 2)      AS media_ciencias_natureza,
            ROUND(AVG(nu_nota_ch)::numeric, 2)      AS media_ciencias_humanas,
            ROUND(AVG(nu_nota_lc)::numeric, 2)      AS media_linguagens,
            ROUND(AVG(nu_nota_redacao)::numeric, 2) AS media_redacao,
            ROUND(AVG(
                (COALESCE(nu_nota_mt, 0) +
                 COALESCE(nu_nota_cn, 0) +
                 COALESCE(nu_nota_ch, 0) +
                 COALESCE(nu_nota_lc, 0) +
                 COALESCE(nu_nota_redacao, 0)) / 5.0
            )::numeric, 2)                          AS media_geral
        FROM silver.enem_2023
        WHERE in_treineiro = false
          AND sg_uf_prova IS NOT NULL
        GROUP BY sg_uf_prova
        ORDER BY media_geral DESC;
    """
    with conn.cursor() as cur:
        cur.execute(sql_read)
        rows = cur.fetchall()

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE gold.desempenho_por_uf;")
        execute_values(cur, """
            INSERT INTO gold.desempenho_por_uf
            (sg_uf, total_participantes, media_matematica,
             media_ciencias_natureza, media_ciencias_humanas,
             media_linguagens, media_redacao, media_geral)
            VALUES %s
        """, rows)
    conn.commit()
    log.info(f" {len(rows)} UFs processadas.")

def build_desempenho_por_faixa_etaria(conn):
    log.info("Calculando KPI: desempenho por faixa etária...")
    sql_read = """
        SELECT
            tp_faixa_etaria,
            COUNT(*)                                AS total_participantes,
            ROUND(AVG(nu_nota_mt)::numeric, 2)      AS media_matematica,
            ROUND(AVG(nu_nota_redacao)::numeric, 2) AS media_redacao,
            ROUND(AVG(
                (COALESCE(nu_nota_mt, 0) +
                 COALESCE(nu_nota_cn, 0) +
                 COALESCE(nu_nota_ch, 0) +
                 COALESCE(nu_nota_lc, 0) +
                 COALESCE(nu_nota_redacao, 0)) / 5.0
            )::numeric, 2)                          AS media_geral
        FROM silver.enem_2023
        WHERE in_treineiro = false
          AND tp_faixa_etaria IS NOT NULL
        GROUP BY tp_faixa_etaria
        ORDER BY tp_faixa_etaria;
    """
    with conn.cursor() as cur:
        cur.execute(sql_read)
        rows = cur.fetchall()

    rows_with_desc = [
        (r[0], FAIXA_ETARIA.get(r[0], "Desconhecida"), r[1], r[2], r[3], r[4])
        for r in rows
    ]

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE gold.desempenho_por_faixa_etaria;")
        execute_values(cur, """
            INSERT INTO gold.desempenho_por_faixa_etaria
            (tp_faixa_etaria, descricao_faixa, total_participantes,
             media_matematica, media_redacao, media_geral)
            VALUES %s
        """, rows_with_desc)
    conn.commit()
    log.info(f"  {len(rows_with_desc)} faixas processadas.")

def build_desempenho_por_escola(conn):
    log.info("Calculando KPI: desempenho por tipo de escola...")
    sql_read = """
        SELECT
            tp_escola,
            COUNT(*)                                AS total_participantes,
            ROUND(AVG(nu_nota_mt)::numeric, 2)      AS media_matematica,
            ROUND(AVG(nu_nota_redacao)::numeric, 2) AS media_redacao,
            ROUND(AVG(
                (COALESCE(nu_nota_mt, 0) +
                 COALESCE(nu_nota_cn, 0) +
                 COALESCE(nu_nota_ch, 0) +
                 COALESCE(nu_nota_lc, 0) +
                 COALESCE(nu_nota_redacao, 0)) / 5.0
            )::numeric, 2)                          AS media_geral,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE nu_nota_mt > 700)
                / NULLIF(COUNT(*), 0)
            , 2)                                    AS perc_nota_acima_700
        FROM silver.enem_2023
        WHERE in_treineiro = false
          AND tp_escola IS NOT NULL
        GROUP BY tp_escola
        ORDER BY tp_escola;
    """
    with conn.cursor() as cur:
        cur.execute(sql_read)
        rows = cur.fetchall()

    rows_with_desc = [
        (r[0], TIPO_ESCOLA.get(r[0], "Desconhecido"),
         r[1], r[2], r[3], r[4], r[5])
        for r in rows
    ]

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE gold.desempenho_por_escola;")
        execute_values(cur, """
            INSERT INTO gold.desempenho_por_escola
            (tp_escola, descricao_escola, total_participantes,
             media_matematica, media_redacao, media_geral,
             perc_nota_acima_700)
            VALUES %s
        """, rows_with_desc)
    conn.commit()
    log.info(f"  {len(rows_with_desc)} tipos de escola processados.")

def build_distribuicao_redacao(conn):
    log.info("Calculando KPI: distribuição de notas de redação...")
    sql_read = """
        WITH faixas AS (
            SELECT
                CASE
                    WHEN nu_nota_redacao IS NULL    THEN '0 - Ausente/Nulo'
                    WHEN nu_nota_redacao = 0        THEN '1 - Nota zero'
                    WHEN nu_nota_redacao < 200      THEN '2 - Até 200'
                    WHEN nu_nota_redacao < 400      THEN '3 - 200 a 399'
                    WHEN nu_nota_redacao < 600      THEN '4 - 400 a 599'
                    WHEN nu_nota_redacao < 800      THEN '5 - 600 a 799'
                    WHEN nu_nota_redacao < 1000     THEN '6 - 800 a 999'
                    ELSE                                 '7 - Nota 1000'
                END AS faixa_nota,
                COUNT(*) AS total
            FROM silver.enem_2023
            WHERE in_treineiro = false
            GROUP BY faixa_nota
        )
        SELECT
            faixa_nota,
            SUBSTRING(faixa_nota, 1, 1)::smallint  AS ordem,
            total                                   AS total_participantes,
            ROUND(100.0 * total / SUM(total) OVER (), 2) AS percentual
        FROM faixas
        ORDER BY ordem;
    """
    with conn.cursor() as cur:
        cur.execute(sql_read)
        rows = cur.fetchall()

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE gold.distribuicao_redacao;")
        execute_values(cur, """
            INSERT INTO gold.distribuicao_redacao
            (faixa_nota, ordem, total_participantes, percentual)
            VALUES %s
        """, rows)
    conn.commit()
    log.info(f"  {len(rows)} faixas de redação processadas.")

def main():
    log.info("=== Iniciando build Gold — ENEM 2023 ===")
    conn = get_connection()

    build_desempenho_por_uf(conn)
    build_desempenho_por_faixa_etaria(conn)
    build_desempenho_por_escola(conn)
    build_distribuicao_redacao(conn)

    conn.close()
    log.info("=== Gold concluída ===")

if __name__ == "__main__":
    main()