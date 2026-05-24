-- =============================================================================
-- Query: lending/05-unified-hhi
-- Question: Sector HHI (Herfindahl-Hirschman Index) using a CONSISTENT
--           metric across all protocols — solves the "market share depends
--           on which source you look at" problem that DefiLlama can produce.
-- Inputs:
--   {{protocols}}     — list, e.g. ['aave_v3', 'compound_v3', 'morpho']
--   {{chain}}         — e.g. 'ethereum'
--   {{snapshot_date}} — default current_date - 1 day
--   {{metric}}        — which metric to compute share by:
--                       'active_borrows_usd' (recommended — measures who's
--                         really facilitating utility, not just sitting on
--                         capital)
--                       'supply_usd' (capital pool size)
--                       'revenue_30d_usd' (revenue dominance)
-- Output schema:
--   protocol      (text)
--   metric_value  (double)
--   market_share  (double — % of total)
--   hhi_contrib   (double — share^2 × 10000, summed gives HHI)
-- Plus one summary row with HHI total at the bottom.
-- =============================================================================
-- ⚠️ Schema-drift warning: the goal here is consistency. Use the SAME table
--    pattern for each protocol (e.g. all from `<protocol>_<chain>.daily`).
--    If one protocol's data has to come from a different source, the HHI
--    becomes meaningless. Better to drop that protocol from the comparison
--    than to mix sources.
-- =============================================================================
-- HHI interpretation:
--   <1500    competitive (multi-strong)
--   1500-2500 moderately concentrated
--   2500-7500 highly concentrated (oligopoly)
--   >7500    near-monopoly
-- =============================================================================

WITH protocol_metrics AS (
    -- Build one row per protocol with the chosen metric.
    -- Replace each block with the actual aggregate table.
    SELECT 'aave_v3' AS protocol,
           SUM(CASE WHEN '{{metric}}' = 'active_borrows_usd' THEN borrow_usd
                    WHEN '{{metric}}' = 'supply_usd'         THEN supply_usd
                    WHEN '{{metric}}' = 'revenue_30d_usd'    THEN revenue_30d_usd
               END) AS metric_value
    FROM {{aave_v3_daily_table}}
    WHERE day = date('{{snapshot_date}}') AND blockchain = '{{chain}}'

    UNION ALL

    SELECT 'compound_v3' AS protocol,
           SUM(CASE WHEN '{{metric}}' = 'active_borrows_usd' THEN borrow_usd
                    WHEN '{{metric}}' = 'supply_usd'         THEN supply_usd
                    WHEN '{{metric}}' = 'revenue_30d_usd'    THEN revenue_30d_usd
               END) AS metric_value
    FROM {{compound_v3_daily_table}}
    WHERE day = date('{{snapshot_date}}') AND blockchain = '{{chain}}'

    UNION ALL

    SELECT 'morpho' AS protocol,
           SUM(CASE WHEN '{{metric}}' = 'active_borrows_usd' THEN borrow_usd
                    WHEN '{{metric}}' = 'supply_usd'         THEN supply_usd
                    WHEN '{{metric}}' = 'revenue_30d_usd'    THEN revenue_30d_usd
               END) AS metric_value
    FROM {{morpho_daily_table}}
    WHERE day = date('{{snapshot_date}}') AND blockchain = '{{chain}}'

    -- Add more protocols here as needed: spark, fluid, etc.
),
shares AS (
    SELECT
        protocol,
        metric_value,
        100.0 * metric_value / SUM(metric_value) OVER () AS market_share
    FROM protocol_metrics
    WHERE metric_value > 0
)
SELECT
    protocol,
    metric_value,
    market_share,
    POWER(market_share, 2) AS hhi_contrib
FROM shares

UNION ALL

-- Total HHI as the final row.
SELECT
    'TOTAL_HHI' AS protocol,
    NULL,
    NULL,
    SUM(POWER(market_share, 2))
FROM shares

ORDER BY hhi_contrib DESC NULLS LAST;

-- =============================================================================
-- Interpretation guide:
-- - Run with `metric = 'active_borrows_usd'` first (recommended default).
--   This shows who's actually generating useful economic activity, not
--   just who has the most capital deposited.
-- - Re-run with `metric = 'supply_usd'` and compare. If one protocol's
--   borrow share is much higher than its supply share, it's using its
--   capital base more efficiently (good capital-velocity signal).
-- - Re-run with `metric = 'revenue_30d_usd'` to see who's actually
--   monetizing. Aave often dominates revenue share even when newer
--   protocols are taking supply share (because Aave's take rate is higher).
-- - Three runs give a triangulation: where does the protocol have a
--   disproportionate share of (capital | activity | revenue)?
-- =============================================================================
