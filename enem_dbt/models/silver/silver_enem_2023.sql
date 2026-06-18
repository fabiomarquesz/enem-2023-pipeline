-- Silver: dados limpos e tipados
-- Referencia o staging via ref() — dbt gerencia a dependência

WITH source AS (
    SELECT * FROM {{ ref('stg_enem_bronze') }}
),

typed AS (
    SELECT
        id                                          AS bronze_id,

        -- Tipagem numérica
        NULLIF(TRIM(nu_inscricao), '')::BIGINT      AS nu_inscricao,
        NULLIF(TRIM(nu_ano), '')::SMALLINT          AS nu_ano,
        NULLIF(TRIM(tp_faixa_etaria), '')::SMALLINT AS tp_faixa_etaria,
        NULLIF(TRIM(tp_sexo), '')::CHAR(1)          AS tp_sexo,
        NULLIF(TRIM(tp_estado_civil), '')::SMALLINT AS tp_estado_civil,
        NULLIF(TRIM(tp_cor_raca), '')::SMALLINT     AS tp_cor_raca,
        NULLIF(TRIM(tp_nacionalidade), '')::SMALLINT AS tp_nacionalidade,
        NULLIF(TRIM(tp_st_conclusao), '')::SMALLINT AS tp_st_conclusao,
        NULLIF(TRIM(tp_ano_concluiu), '')::SMALLINT AS tp_ano_concluiu,
        NULLIF(TRIM(tp_escola), '')::SMALLINT       AS tp_escola,
        NULLIF(TRIM(tp_ensino), '')::SMALLINT       AS tp_ensino,

        -- Boolean
        CASE WHEN TRIM(in_treineiro) = '1' THEN TRUE
             WHEN TRIM(in_treineiro) = '0' THEN FALSE
             ELSE NULL END                          AS in_treineiro,

        -- Escola
        NULLIF(TRIM(co_municipio_esc), '')::INTEGER AS co_municipio_esc,
        NULLIF(TRIM(no_municipio_esc), '')          AS no_municipio_esc,
        NULLIF(TRIM(co_uf_esc), '')::SMALLINT       AS co_uf_esc,
        NULLIF(TRIM(sg_uf_esc), '')::CHAR(2)        AS sg_uf_esc,
        NULLIF(TRIM(tp_dependencia_adm_esc), '')::SMALLINT AS tp_dependencia_adm_esc,
        NULLIF(TRIM(tp_localizacao_esc), '')::SMALLINT     AS tp_localizacao_esc,
        NULLIF(TRIM(tp_sit_func_esc), '')::SMALLINT        AS tp_sit_func_esc,

        -- Local de prova
        NULLIF(TRIM(co_municipio_prova), '')::INTEGER AS co_municipio_prova,
        NULLIF(TRIM(no_municipio_prova), '')          AS no_municipio_prova,
        NULLIF(TRIM(co_uf_prova), '')::SMALLINT       AS co_uf_prova,
        NULLIF(TRIM(sg_uf_prova), '')::CHAR(2)        AS sg_uf_prova,

        -- Notas (vírgula → ponto)
        NULLIF(REPLACE(TRIM(nu_nota_cn), ',', '.'), '')::NUMERIC(6,2)      AS nu_nota_cn,
        NULLIF(REPLACE(TRIM(nu_nota_ch), ',', '.'), '')::NUMERIC(6,2)      AS nu_nota_ch,
        NULLIF(REPLACE(TRIM(nu_nota_lc), ',', '.'), '')::NUMERIC(6,2)      AS nu_nota_lc,
        NULLIF(REPLACE(TRIM(nu_nota_mt), ',', '.'), '')::NUMERIC(6,2)      AS nu_nota_mt,
        NULLIF(REPLACE(TRIM(nu_nota_redacao), ',', '.'), '')::NUMERIC(6,2) AS nu_nota_redacao,

        -- Presença
        NULLIF(TRIM(tp_presenca_cn), '')::SMALLINT  AS tp_presenca_cn,
        NULLIF(TRIM(tp_presenca_ch), '')::SMALLINT  AS tp_presenca_ch,
        NULLIF(TRIM(tp_presenca_lc), '')::SMALLINT  AS tp_presenca_lc,
        NULLIF(TRIM(tp_presenca_mt), '')::SMALLINT  AS tp_presenca_mt,
        NULLIF(TRIM(tp_lingua), '')::SMALLINT       AS tp_lingua,
        NULLIF(TRIM(tp_status_redacao), '')::SMALLINT AS tp_status_redacao,

        -- Questionário
        NULLIF(TRIM(q001), '')::CHAR(1) AS q001,
        NULLIF(TRIM(q002), '')::CHAR(1) AS q002,
        NULLIF(TRIM(q003), '')::CHAR(1) AS q003,
        NULLIF(TRIM(q004), '')::CHAR(1) AS q004,
        NULLIF(TRIM(q005), '')::CHAR(1) AS q005,
        NULLIF(TRIM(q006), '')::CHAR(1) AS q006,

        ingested_at,
        NOW() AS transformed_at

    FROM source
)

SELECT * FROM typed
