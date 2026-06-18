WITH silver AS (
    SELECT * FROM {{ ref('silver_enem_2023') }}
    WHERE in_treineiro = FALSE
      AND sg_uf_prova IS NOT NULL
)

SELECT
    sg_uf_prova                                     AS sg_uf,
    COUNT(*)                                        AS total_participantes,
    ROUND(AVG(nu_nota_mt)::NUMERIC, 2)              AS media_matematica,
    ROUND(AVG(nu_nota_cn)::NUMERIC, 2)              AS media_ciencias_natureza,
    ROUND(AVG(nu_nota_ch)::NUMERIC, 2)              AS media_ciencias_humanas,
    ROUND(AVG(nu_nota_lc)::NUMERIC, 2)              AS media_linguagens,
    ROUND(AVG(nu_nota_redacao)::NUMERIC, 2)         AS media_redacao,
    ROUND(AVG(
        (COALESCE(nu_nota_mt, 0) +
         COALESCE(nu_nota_cn, 0) +
         COALESCE(nu_nota_ch, 0) +
         COALESCE(nu_nota_lc, 0) +
         COALESCE(nu_nota_redacao, 0)) / 5.0
    )::NUMERIC, 2)                                  AS media_geral,
    NOW()                                           AS atualizado_em
FROM silver
GROUP BY sg_uf_prova
ORDER BY media_geral DESC
