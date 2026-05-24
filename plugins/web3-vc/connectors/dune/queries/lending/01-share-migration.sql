-- =============================================================================
-- Query: lending/01-share-migration
-- Question: Are wallets actively moving deposits between major lending
--           protocols, and which direction? (Porter Force 1: rivalry — measures
--           share migration's first-order derivative, not just snapshot share.)
-- Inputs:
--   {{from_protocol}}     — e.g. 'aave_v3' (the protocol losing flow)
--   {{to_protocol}}       — e.g. 'morpho'  (the protocol gaining flow)
--   {{lookback_days}}     — window to scan (default 30)
--   {{migration_window_hours}} — same wallet must show withdraw → deposit
--                               within this window to count (default 24)
-- Output schema:
--   day                 (date)
--   from_protocol       (text)
--   to_protocol         (text)
--   migrated_addresses  (uint  — number of distinct wallets)
--   migrated_usd        (double — total USD value of migration that day)
-- =============================================================================
-- ⚠️ Schema-drift warning: Spellbook table names evolve. Before running:
--    Use Dune MCP `searchTables` for "aave v3" / "morpho" to confirm the
--    current event-table names and column conventions for your target chain.
--    Common patterns: `aave_v3_ethereum.supply`, `aave_v3_ethereum.withdraw`,
--    `morpho_blue_ethereum.supply`, etc.
-- =============================================================================

-- Skeleton (adapt table names + column names to current Spellbook):

WITH withdrawals AS (
    -- All withdraw events from {{from_protocol}} on Ethereum in the window.
    -- Adapt this CTE to the actual withdraw-event table for the protocol.
    SELECT
        evt_block_time      AS withdraw_time,
        user                AS wallet,
        amount * p.price    AS usd_value  -- join to prices.usd for USD
    FROM {{from_protocol_table_withdraw}}  -- e.g. aave_v3_ethereum.withdraw
    LEFT JOIN prices.usd p
        ON p.contract_address = reserve   -- column name varies by protocol
        AND p.minute = date_trunc('minute', evt_block_time)
        AND p.blockchain = 'ethereum'
    WHERE evt_block_time >= now() - interval '{{lookback_days}}' day
),
deposits AS (
    -- Same pattern, but for deposits into {{to_protocol}}.
    SELECT
        evt_block_time      AS deposit_time,
        on_behalf_of        AS wallet,
        amount * p.price    AS usd_value
    FROM {{to_protocol_table_supply}}      -- e.g. morpho_blue_ethereum.supply
    LEFT JOIN prices.usd p
        ON p.contract_address = market  -- column name varies
        AND p.minute = date_trunc('minute', evt_block_time)
        AND p.blockchain = 'ethereum'
    WHERE evt_block_time >= now() - interval '{{lookback_days}}' day
)
SELECT
    date_trunc('day', w.withdraw_time)              AS day,
    '{{from_protocol}}'                              AS from_protocol,
    '{{to_protocol}}'                                AS to_protocol,
    COUNT(DISTINCT w.wallet)                         AS migrated_addresses,
    SUM(LEAST(w.usd_value, d.usd_value))             AS migrated_usd
FROM withdrawals w
INNER JOIN deposits d
    ON w.wallet = d.wallet
    AND d.deposit_time BETWEEN w.withdraw_time
        AND w.withdraw_time + interval '{{migration_window_hours}}' hour
GROUP BY 1
ORDER BY day DESC;

-- =============================================================================
-- Interpretation guide (for skill to apply):
-- - If `migrated_usd` trend is rising — the rivalry pressure on
--   {{from_protocol}} is intensifying; flag a 🟡 or 🔴 on Force 1.
-- - If migration is large but `migrated_addresses` is small (e.g. <10),
--   it's a few large wallets — investigate whether they're MM / treasury
--   ops (could be noise) vs. real demand-side rotation.
-- - Compare with `02-deposit-concentration.sql` output: if the migrating
--   wallets are also top-10 LPs at {{from_protocol}}, the protocol is
--   losing its most valuable customers, not retail dust.
-- =============================================================================
