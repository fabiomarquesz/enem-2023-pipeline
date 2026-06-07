-- Schemas da Medallion Architecture
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Tabela Bronze: dados brutos do ENEM 2023
-- Tudo como TEXT — na Bronze não fazemos suposições sobre os dados
CREATE TABLE IF NOT EXISTS bronze.enem_2023 (
    id                  SERIAL PRIMARY KEY,
    nu_inscricao        TEXT,
    nu_ano              TEXT,
    tp_faixa_etaria     TEXT,
    tp_sexo             TEXT,
    tp_estado_civil     TEXT,
    tp_cor_raca         TEXT,
    tp_nacionalidade    TEXT,
    tp_st_conclusao     TEXT,
    tp_ano_concluiu     TEXT,
    tp_escola           TEXT,
    tp_ensino           TEXT,
    in_treineiro        TEXT,
    co_municipio_esc    TEXT,
    no_municipio_esc    TEXT,
    co_uf_esc           TEXT,
    sg_uf_esc           TEXT,
    tp_dependencia_adm_esc TEXT,
    tp_localizacao_esc  TEXT,
    tp_sit_func_esc     TEXT,
    co_municipio_prova  TEXT,
    no_municipio_prova  TEXT,
    co_uf_prova         TEXT,
    sg_uf_prova         TEXT,
    nu_nota_cn          TEXT,
    nu_nota_ch          TEXT,
    nu_nota_lc          TEXT,
    nu_nota_mt          TEXT,
    nu_nota_redacao     TEXT,
    tp_presenca_cn      TEXT,
    tp_presenca_ch      TEXT,
    tp_presenca_lc      TEXT,
    tp_presenca_mt      TEXT,
    tp_lingua           TEXT,
    tp_status_redacao   TEXT,
    q001                TEXT,
    q002                TEXT,
    q003                TEXT,
    q004                TEXT,
    q005                TEXT,
    q006                TEXT,
    ingested_at         TIMESTAMP DEFAULT NOW()
);

-- Index para buscas comuns
CREATE INDEX IF NOT EXISTS idx_enem_bronze_uf 
    ON bronze.enem_2023(sg_uf_prova);
CREATE INDEX IF NOT EXISTS idx_enem_bronze_inscricao 
    ON bronze.enem_2023(nu_inscricao);

