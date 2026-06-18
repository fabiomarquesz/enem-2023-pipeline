WITH silver AS (
    SELECT * FROM {{ ref('silver_enem_2023') }}
    WHERE in_treineiro = FALSE
      AND tp_escola IS NOT NULL
),

descricao AS (
    SELECT
        tp_escola,
        CASE tp_escola
            WHEN 1 THEN 'Não respondeu'
            WHEN 2 THEN 'Pública'
            WHEN 3 THEN 'Privada'
            ELSE 'Desconhecido'
        END AS descricao_escola
    FROM silver
    GROUP BY tp_escola
)

SELECT
    s.tp_escola,
    d.descricao_escola,
    COUNT(*)                                        AS total_participantes,
    ROUND(AVG(s.nu_nota_mt)::NUMERIC, 2)            AS media_matematica,
    ROUND(AVG(s.nu_nota_redacao)::NUMERIC, 2)       AS media_redacao,
    ROUND(AVG(
        (COALESCE(s.nu_nota_mt, 0) +
         COALESCE(s.nu_nota_cn, 0) +
         COALESCE(s.nu_nota_ch, 0) +
         COALESCE(s.nu_nota_lc, 0) +
         COALESCE(s.nu_nota_redacao, 0)) / 5.0
    )::NUMERIC, 2)                                  AS media_geral,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE s.nu_nota_mt > 700)
        / NULLIF(COUNT(*), 0)
    , 2)                                            AS perc_nota_acima_700,
    NOW()                                           AS atualizado_em
FROM silver s
JOIN descricao d ON s.tp_escola = d.tp_escola
GROUP BY s.tp_escola, d.descricao_escola
ORDER BY s.tp_escola
