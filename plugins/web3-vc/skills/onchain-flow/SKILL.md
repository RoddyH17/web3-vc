---
name: onchain-flow
description: "[Phase 1 stub] On-chain microstructure analysis — LP retention, trader cohorts, MM concentration, MEV extraction, JIT events. Runs curated Dune SQL queries against a target protocol. Not yet implemented in Phase 0."
---

# On-chain Flow Analysis (Phase 1 — NOT IMPLEMENTED)

## Status: STUB

This skill is scaffolded for design clarity but **not functional in Phase 0**. Invoking it will surface this notice.

## Phase 1 plan

### Connector dependency
- Dune Analytics MCP wrapper (REST API; free tier 1000 req/month is sufficient for personal use).

### Query library (to be authored)
Curated Dune SQL templates, one file per query under `connectors/dune/queries/`:

1. **lp-cohort-retention.sql** — for a given AMM, what % of LPs added in month N are still providing liquidity in month N+1, +3, +6?
2. **trader-pareto.sql** — Gini coefficient of trader fee contribution; flags whether protocol is wash-trade-driven.
3. **mm-concentration.sql** — for perp DEX / intent solver networks, what share of fills comes from top 3 / top 10 entities?
4. **mev-extraction.sql** — sandwich attack frequency and value extracted from a given DEX in the past 30d.
5. **jit-liquidity.sql** — for V3-style CLMM, how many fills are captured by JIT (just-in-time) liquidity bots?
6. **incentive-attribution.sql** — what % of TVL leaves within N blocks of incentive cessation?
7. **real-user-cohort.sql** — distinct active addresses by week, excluding known bot / sybil clusters.

### Skill workflow (planned)
1. User invokes `/onchain {protocol}` or `/onchain {query-name} {protocol}`
2. Skill maps protocol → contract addresses (cached locally or fetched from DefiLlama)
3. Runs the relevant Dune query via MCP
4. Returns a structured markdown report with the SQL result + interpretation framework
5. Writes output to `./onchain/{protocol}-{query}-{YYYY-MM-DD}.md`

### Design intent

The skill intentionally **constrains** to the curated query library. Open-ended SQL generation by Claude is risky (hallucinated table names, schema drift). Instead, this skill is a structured runner over human-authored queries — the user (or contributors) adds new SQL files; the skill makes them invokable.

## Triggers (so this skill is discoverable when invoked)

"on-chain analysis", "LP retention", "trader cohorts", "MEV extraction", "JIT liquidity", "smart money flow", "Dune query", "microstructure"
