-- =============================================================================
-- Query: lending/03-utilization-trend
-- Question: Daily utilization (borrows / supply) per protocol over the
--           lookback window. Answers Porter Force 1 question about how
--           productively capital is being used, and whether protocols are
--           competing on the same demand.
-- Inputs:
--   {{protocols}}     — list, e.g. ARRAY['aave_v3', 'compound_v3', 'morpho']
--   {{chain}}         — e.g. 'ethereum'
--   {{lookback_days}} — default 30
-- Output schema:
--   day              (date)
--   protocol         (text)
--   total_supply_usd (double)
--   total_borrow_usd (double)
--   utilization_pct  (double)
-- =============================================================================
-- ⚠️ Schema-drift warning: Spellbook has aggregate-daily views for major
--    lending protocols (e.g. `aave_v3_ethereum.protocol_daily_metrics`).
--    Prefer these over re-aggregating raw events — they're materialized
--    and cached, so the query runs in seconds instead of minutes.
--    Run `searchTables` for "<protocol>_<chain> daily" to find the
--    canonical aggregate.
-- =============================================================================

-- Pattern: one CTE per protocol, then UNION ALL into a long-format result.
-- This skeleton uses pseudo-table names; replace each block with the
-- correct Spellbook aggregate table for that protocol.

WITH aave_v3 AS (
    SELECT
        day,
        'aave_v3'                                AS protocol,
        SUM(supply_usd)                          AS total_supply_usd,
        SUM(borrow_usd)                          AS total_borrow_usd
    FROM {{aave_v3_daily_table}}                  -- e.g. aave_v3_ethereum.daily
    WHERE day >= current_date - interval '{{lookback_days}}' day
        AND blockchain = '{{chain}}'
    GROUP BY 1
),
compound_v3 AS (
    SELECT
        day,
        'compound_v3'                            AS protocol,
        SUM(supply_usd)                          AS total_supply_usd,
        SUM(borrow_usd)                          AS total_borrow_usd
    FROM {{compound_v3_daily_table}}
    WHERE day >= current_date - interval '{{lookback_days}}' day
        AND blockchain = '{{chain}}'
    GROUP BY 1
),
morpho AS (
    SELECT
        day,
        'morpho'                                 AS protocol,
        SUM(supply_usd)                          AS total_supply_usd,
        SUM(borrow_usd)                          AS total_borrow_usd
    FROM {{morpho_daily_table}}
    WHERE day >= current_date - interval '{{lookback_days}}' day
        AND blockchain = '{{chain}}'
    GROUP BY 1
)
SELECT
    day,
    protocol,
    total_supply_usd,
    total_borrow_usd,
    100.0 * total_borrow_usd / NULLIF(total_supply_usd, 0)  AS utilization_pct
FROM (
    SELECT * FROM aave_v3
    UNION ALL
    SELECT * FROM compound_v3
    UNION ALL
    SELECT * FROM morpho
)
ORDER BY day DESC, protocol;

-- =============================================================================
-- Interpretation guide:
-- - Healthy utilization band: 60–80% (Aave shows ~77% in steady state).
-- - <40% → capital sitting idle, protocol may not have demand-side PMF.
-- - >90% → liquidity stress; supply withdrawals may be blocked.
-- - Cross-protocol comparison: if all protocols rise/fall together, demand
--   is sector-wide (rate cycle, macro). If one rises while others fall, the
--   rising one is **stealing** demand — strongly bullish for it, bearish
--   for the others.
-- - Compare with `01-share-migration.sql` to confirm whether utilization
--   shifts correspond to actual wallet movements.
-- =============================================================================
