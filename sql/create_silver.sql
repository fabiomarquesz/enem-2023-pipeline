-- Tabela Silver - dados limpos e enriquecidos
CREATE TABLE IF NOT EXISTS silver.enem_2023 (
    id SERIAL PRIMARY KEY,
    
    -- Identificação
    nu_inscricao BIGINT,
    nu_ano SMALLINT,

    -- Perfil do candidato
    tp_faixa_etaria SMALLINT,
    tp_sexo CHAR(1),
    tp_estado_civil SMALLINT,
    tp_cor_raca SMALLINT,
    tp_nacionalidade SMALLINT,

    -- Situação escolar
    tp_st_conclusao SMALLINT,
    tp_ano_concluiu SMALLINT,
    tp_escola SMALLINT,
    tp_ensino SMALLINT,
    in_treineiro BOOLEAN,

    -- Escola
    co_municipio_esc INTEGER,
    no_municipio_esc TEXT,
    co_uf_esc SMALLINT,
    sg_uf_esc CHAR(2),
    tp_dependencia_adm_esc SMALLINT,
    tp_localizacao_esc SMALLINT,
    tp_sit_func_esc SMALLINT,

    -- Local de prova
    co_municipio_prova INTEGER,
    no_municipio_prova TEXT,
    co_uf_prova SMALLINT,
    sg_uf_prova CHAR(2),

    -- Notas
    nu_nota_cn NUMERIC(6,2),
    nu_nota_ch NUMERIC(6,2),
    nu_nota_lc NUMERIC(6,2),
    nu_nota_mt NUMERIC(6,2),
    nu_nota_redacao NUMERIC(6,2),

    -- Presença
    tp_presenca_cn SMALLINT,
    tp_presenca_ch SMALLINT,
    tp_presenca_lc SMALLINT,
    tp_presenca_mt SMALLINT,

    -- Língua e redação
    tp_lingua SMALLINT,
    tp_status_redacao SMALLINT,

    -- Questionário socioeconômico (amostra)
    q001 CHAR(1),
    q002 CHAR(1),
    q003 CHAR(1),
    q004 CHAR(1),
    q005 CHAR(1),
    q006 CHAR(1),
    
    -- Controle de qualidade
    bronze_id INTEGER,
    transformed_at TIMESTAMP DEFAULT NOW()
);

-- Índices para queries analíticas
CREATE INDEX IF NOT EXISTS idx_silver_uf_prova
    ON silver.enem_2023 (sg_uf_prova);

CREATE INDEX IF NOT EXISTS idx_silver_nota_mt
    ON silver.enem_2023 (nu_nota_mt);

CREATE INDEX IF NOT EXISTS idx_silver_nota_redacao
    ON silver.enem_2023 (nu_nota_redacao);

CREATE INDEX IF NOT EXISTS idx_silver_treineiro
    ON silver.enem_2023 (in_treineiro);
