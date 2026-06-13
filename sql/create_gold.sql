
-- KPI 1: Desempenho médio por UF
CREATE TABLE IF NOT EXISTS gold.desempenho_por_uf (
    sg_uf                   CHAR(2) PRIMARY KEY,
    total_participantes     INTEGER,
    media_matematica        NUMERIC(6,2),
    media_ciencias_natureza NUMERIC(6,2),
    media_ciencias_humanas  NUMERIC(6,2),
    media_linguagens        NUMERIC(6,2),
    media_redacao           NUMERIC(6,2),
    media_geral             NUMERIC(6,2),
    atualizado_em           TIMESTAMP DEFAULT NOW()
);

-- KPI 2: Desempenho por faixa etária
CREATE TABLE IF NOT EXISTS gold.desempenho_por_faixa_etaria (
    tp_faixa_etaria         SMALLINT PRIMARY KEY,
    descricao_faixa         TEXT,
    total_participantes     INTEGER,
    media_matematica        NUMERIC(6,2),
    media_redacao           NUMERIC(6,2),
    media_geral             NUMERIC(6,2),
    atualizado_em           TIMESTAMP DEFAULT NOW()
);

-- KPI 3: Desempenho por tipo de escola
CREATE TABLE IF NOT EXISTS gold.desempenho_por_escola (
    tp_escola               SMALLINT PRIMARY KEY,
    descricao_escola        TEXT,
    total_participantes     INTEGER,
    media_matematica        NUMERIC(6,2),
    media_redacao           NUMERIC(6,2),
    media_geral             NUMERIC(6,2),
    perc_nota_acima_700     NUMERIC(5,2),
    atualizado_em           TIMESTAMP DEFAULT NOW()
);

-- KPI 4: Distribuição de notas de redação
CREATE TABLE IF NOT EXISTS gold.distribuicao_redacao (
    faixa_nota              TEXT PRIMARY KEY,
    ordem                   SMALLINT,
    total_participantes     INTEGER,
    percentual              NUMERIC(5,2),
    atualizado_em           TIMESTAMP DEFAULT NOW()
);

