-- =============================================================================
-- Query: lending/04-liquidation-volume
-- Question: Liquidation events $ volume per protocol over time.
--           Answers two things:
--           1. (Porter Force 5: supplier power → reliability of oracle infra)
--              Liquidation cascades = oracle / matching engine stress test.
--           2. Risk health — recurring large liquidations suggest
--              risk-parameter calibration issues.
-- Inputs:
--   {{protocols}}     — list, e.g. ['aave_v3', 'compound_v3', 'morpho']
--   {{chain}}         — e.g. 'ethereum'
--   {{lookback_days}} — default 90 (longer window to catch event clusters)
-- Output schema:
--   day                       (date)
--   protocol                  (text)
--   liquidations_count        (int)
--   liquidated_collateral_usd (double — total seized)
--   liquidator_profit_usd     (double — bonus paid to liquidators)
--   bad_debt_residual_usd     (double — collateral seizure - debt repaid;
--                              negative = bad debt absorbed by protocol)
-- =============================================================================
-- ⚠️ Schema-drift warning: liquidation event tables for each protocol have
--    different schemas. Run `searchTables` for
--    "<protocol> liquidation" before composing the actual query.
--    Common names: `aave_v3_ethereum.liquidationcall`,
--    `compound_v3_ethereum.absorbcollateral`, `morpho_blue_ethereum.liquidate`.
-- =============================================================================

WITH aave_liquidations AS (
    SELECT
        date_trunc('day', evt_block_time)        AS day,
        'aave_v3'                                AS protocol,
        COUNT(*)                                 AS liquidations_count,
        SUM(collateral_amount * cp.price)        AS liquidated_collateral_usd,
        SUM(liquidator_bonus * cp.price)         AS liquidator_profit_usd,
        SUM((collateral_amount - debt_to_cover) * cp.price) AS bad_debt_residual_usd
    FROM {{aave_v3_liquidation_table}}            -- e.g. aave_v3_ethereum.liquidationcall
    LEFT JOIN prices.usd cp
        ON cp.contract_address = collateral_asset
        AND cp.minute = date_trunc('minute', evt_block_time)
        AND cp.blockchain = '{{chain}}'
    WHERE evt_block_time >= current_date - interval '{{lookback_days}}' day
    GROUP BY 1
),
compound_liquidations AS (
    SELECT
        date_trunc('day', evt_block_time)        AS day,
        'compound_v3'                            AS protocol,
        COUNT(*)                                 AS liquidations_count,
        SUM(collateral_amount * cp.price)        AS liquidated_collateral_usd,
        0                                        AS liquidator_profit_usd,   -- adapt
        0                                        AS bad_debt_residual_usd    -- adapt
    FROM {{compound_v3_liquidation_table}}
    LEFT JOIN prices.usd cp
        ON cp.contract_address = collateral_asset
        AND cp.minute = date_trunc('minute', evt_block_time)
        AND cp.blockchain = '{{chain}}'
    WHERE evt_block_time >= current_date - interval '{{lookback_days}}' day
    GROUP BY 1
),
morpho_liquidations AS (
    SELECT
        date_trunc('day', evt_block_time)        AS day,
        'morpho'                                 AS protocol,
        COUNT(*)                                 AS liquidations_count,
        SUM(collateral_amount * cp.price)        AS liquidated_collateral_usd,
        0                                        AS liquidator_profit_usd,
        0                                        AS bad_debt_residual_usd
    FROM {{morpho_liquidation_table}}
    LEFT JOIN prices.usd cp
        ON cp.contract_address = collateral_asset
        AND cp.minute = date_trunc('minute', evt_block_time)
        AND cp.blockchain = '{{chain}}'
    WHERE evt_block_time >= current_date - interval '{{lookback_days}}' day
    GROUP BY 1
)
SELECT * FROM aave_liquidations
UNION ALL
SELECT * FROM compound_liquidations
UNION ALL
SELECT * FROM morpho_liquidations
ORDER BY day DESC, liquidated_collateral_usd DESC;

-- =============================================================================
-- Interpretation guide:
-- - Daily liquidation_usd normally <0.5% of TVL on stable days. Spikes to
--   >5% indicate cascade events (e.g. LST depeg, large oracle deviation,
--   leveraged farm unwind).
-- - bad_debt_residual_usd > 0 on a single day is normal noise; persistent
--   positive sum over 30d is a red flag — protocol's risk parameters are
--   too aggressive or its liquidation engine too slow.
-- - liquidator_profit_usd / liquidated_collateral_usd is the effective
--   liquidation bonus paid. If this is rising (vs the protocol's posted
--   bonus param), it means the protocol is over-incentivizing liquidators
--   to clear positions, often a stress signal.
-- - Cross-protocol pattern: did all protocols spike on the same day?
--   = market event. Did one protocol spike alone? = protocol-specific
--   risk failure (asset listing, oracle config).
-- =============================================================================
