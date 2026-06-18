WITH silver AS (
    SELECT * FROM {{ ref('silver_enem_2023') }}
    WHERE in_treineiro = FALSE
),

faixas AS (
    SELECT
        CASE
            WHEN nu_nota_redacao IS NULL THEN '0 - Ausente/Nulo'
            WHEN nu_nota_redacao = 0     THEN '1 - Nota zero'
            WHEN nu_nota_redacao < 200   THEN '2 - Até 200'
            WHEN nu_nota_redacao < 400   THEN '3 - 200 a 399'
            WHEN nu_nota_redacao < 600   THEN '4 - 400 a 599'
            WHEN nu_nota_redacao < 800   THEN '5 - 600 a 799'
            WHEN nu_nota_redacao < 1000  THEN '6 - 800 a 999'
            ELSE                              '7 - Nota 1000'
        END                             AS faixa_nota,
        COUNT(*)                        AS total_participantes
    FROM silver
    GROUP BY faixa_nota
)

SELECT
    faixa_nota,
    SUBSTRING(faixa_nota, 1, 1)::SMALLINT           AS ordem,
    total_participantes,
    ROUND(100.0 * total_participantes
        / SUM(total_participantes) OVER (), 2)      AS percentual,
    NOW()                                           AS atualizado_em
FROM faixas
ORDER BY ordem
