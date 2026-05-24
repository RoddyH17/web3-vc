-- =============================================================================
-- Query: lending/02-deposit-concentration
-- Question: How concentrated is the protocol's deposit base?
--           (Porter Force 4: buyer power — if top-10 hold 80%+ of TVL,
--           buyer power is concentrated and protocol fragile.)
-- Inputs:
--   {{protocol}}      — e.g. 'aave_v3'
--   {{chain}}         — e.g. 'ethereum'
--   {{top_n}}         — number of top depositors to highlight (default 20)
-- Output schema:
--   rank              (int)
--   address           (text)
--   usd_value         (double)
--   pct_of_total      (double — % of protocol TVL)
--   cumulative_pct    (double — running cumulative %)
--   account_age_days  (int — first interaction with protocol)
-- =============================================================================
-- ⚠️ Schema-drift warning: use `searchTables` to find the actual current
--    balance / position table for your protocol. Many protocols have a
--    pre-computed "user_state" or "positions" table on Spellbook that
--    avoids re-aggregating from raw events (much faster).
-- =============================================================================

WITH current_positions AS (
    -- Sum each user's outstanding deposits across all reserves.
    -- For Aave V3, check tables like aave_v3_{{chain}}.user_state_supply or
    -- aggregate from supply / withdraw / accruedToTreasury events.
    SELECT
        user                                   AS address,
        SUM(supply_amount * price)             AS usd_value
    FROM {{protocol_positions_table}}          -- adapt per protocol
    WHERE chain = '{{chain}}'
        AND supply_amount > 0
    GROUP BY 1
),
ranked AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY usd_value DESC)              AS rank,
        address,
        usd_value,
        100.0 * usd_value / SUM(usd_value) OVER ()               AS pct_of_total,
        100.0 * SUM(usd_value) OVER (
            ORDER BY usd_value DESC ROWS UNBOUNDED PRECEDING
        ) / SUM(usd_value) OVER ()                               AS cumulative_pct
    FROM current_positions
)
SELECT
    r.rank,
    r.address,
    r.usd_value,
    r.pct_of_total,
    r.cumulative_pct,
    -- Optional enrichment: join to first-seen events table for account age.
    -- Skip this block if no age table is convenient.
    DATE_DIFF(
        'day',
        (SELECT MIN(evt_block_time)
         FROM {{protocol_supply_events_table}}
         WHERE user = r.address),
        current_date
    )                                                            AS account_age_days
FROM ranked r
WHERE r.rank <= {{top_n}}
ORDER BY r.rank;

-- =============================================================================
-- Interpretation guide (for skill to apply):
-- - Top-10 cumulative_pct:
--     >80% → 🔴 concentrated, single-actor risk; the "TVL" is really
--             3-5 wallets pretending to be a market
--     50-80% → 🟡 typical for DeFi blue chip; flag if top 1 wallet >30%
--     <50%  → 🟢 distributed depositor base
-- - account_age_days for top wallets:
--     <30 days → mercenary capital chasing recent incentive
--     >365 days → sticky long-term LPs (good sign)
-- - Cross-reference top addresses with Nansen labels (Phase 2) to identify
--   whether they're: institutional MMs, large treasuries, or other protocols
--   (e.g. a "top LP" being Morpho's vault hot-routing through the protocol
--   tells a very different story than retail LPs).
-- =============================================================================
