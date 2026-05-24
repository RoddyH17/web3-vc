# Dune Analytics MCP Connector

This plugin uses **Dune's official remote MCP server** at `https://api.dune.com/mcp/v1` to give Claude direct access to Dune's data warehouse (raw and decoded tables across 100+ blockchains, community Spellbook curations, real-time indexed data).

The connector is wired in `.mcp.json` at the plugin root. There is no local Python wrapper to install — the MCP is hosted by Dune.

## Why we need Dune (in addition to DefiLlama)

**DefiLlama answers "is how much"**: aggregated, pre-computed TVL / fees / revenue, with consistent cross-protocol schemas. Open-the-box, fast, free.

**Dune answers "by whom, how changing, and why"**: the raw event-level link to the chains themselves — every supply event, every borrow, every liquidation, every wallet that moved capital between protocols. You write SQL; Dune runs it against ~3PB of indexed chain data.

The sector skill (`/web3-vc:sector`) uses both: DefiLlama for breadth (covering all protocols in a sector at standard granularity), Dune for depth (share-migration dynamics, deposit concentration, bad-debt events, capital-quality measures).

## Setup

### 1. Get a Dune API key

Sign up at [dune.com](https://dune.com), then visit your account settings → API → create a key. The free tier ("Plus") allows ~1000 query executions / month, which is plenty for a personal research workflow.

### 2. Export `DUNE_API_KEY` in your shell

Add to `~/.zshrc` (or `~/.bashrc`):

```bash
export DUNE_API_KEY="dune_xxxxx_your_key_here"
```

Then `source ~/.zshrc`.

### 3. Restart Claude Code

Required so the env var propagates to the MCP server spawn.

### 4. (Fallback) Hardcode the key if env-var interpolation doesn't work

If `${DUNE_API_KEY}` substitution in `.mcp.json` headers isn't supported by your Claude Code version, edit `.mcp.json` directly and replace the placeholder with your literal key:

```json
"headers": {
  "X-DUNE-API-KEY": "dune_xxxxx_your_actual_key"
}
```

**Warning**: if you do this, the key gets committed to the repo unless you add a `.gitignore` exception. Prefer the env-var path.

### 5. Verify

In Claude Code, ask:

```text
Using the dune MCP, run searchDocs("lending") and show me the first 3 results.
```

If you see Dune docs results, the connector is working.

## Available tools (provided by Dune's MCP server)

Roughly 17 tools across 5 categories. The most-used by this plugin's skills:

| Category | Tool | Purpose |
|---|---|---|
| Discovery | `searchDocs` | search Dune documentation (no credit cost) |
| Discovery | `searchTables` | find indexed tables by keyword (Aave, Compound, etc.) |
| Discovery | `searchTablesByContractAddress` | find tables tracking a specific contract |
| Discovery | `listBlockchains` | list all indexed chains |
| Query | `createDuneQuery` | create a saved query |
| Query | `getDuneQuery` | fetch an existing query by ID |
| Query | `updateDuneQuery` | edit a saved query |
| Query | `executeQueryById` | run a saved query |
| Query | `getExecutionResults` | fetch results of a completed run |
| Viz | `generateVisualization` | chart the result |
| Account | `getUsage` | check credit balance |

For the full list and per-tool specs, see [Dune's MCP docs](https://docs.dune.com/api-reference/agents/mcp).

## Tool timeout warning

Dune's complex SQL queries (especially full-table scans over 30d windows) often run **60–180 seconds**. The default MCP client tool timeout in Claude Code is 60 seconds, which causes `Transport closed` errors mid-query.

**Recommended:** set MCP tool timeout to 300 seconds in your Claude Code settings. See `~/.claude/settings.json` and add:

```json
{
  "mcpToolTimeoutMs": 300000
}
```

(Setting key may vary by Claude Code version — check `/config` if uncertain.)

## SQL template library

The `queries/` subdirectory holds SQL templates organized by sector:

```
connectors/dune/queries/
├── lending/
│   ├── 01-share-migration.sql
│   ├── 02-deposit-concentration.sql
│   ├── 03-utilization-trend.sql
│   ├── 04-liquidation-volume.sql
│   └── 05-unified-hhi.sql
├── perp/             # TBD (Phase 2)
└── dex/              # TBD (Phase 2)
```

Each template:
- Is **parameterized** with placeholders (`{{start_date}}`, `{{protocol_list}}`, etc.)
- Includes a header comment explaining: which sector-three-question it answers, expected inputs/outputs, and Spellbook tables it depends on
- Is **versioned with the schema it was tested against** — Spellbook tables evolve, so re-validate before running on new data

The sector skill loads these templates, parameterizes them, and runs them via Dune MCP's `createDuneQuery` + `executeQueryById`.

## Credit cost discipline

Dune's pricing is per query execution, not per row returned. Practical guidelines for this plugin:

- **Free tier (Plus)**: ~1000 executions / month → enough for ~30 sector scans per month, generous
- **Pro tier**: needed if you start running daily watch jobs (Phase 1 `/web3-vc:watch`)
- Always cache results — re-running the same query within a few hours is waste
- Use the `searchTables` / `searchDocs` tools to explore (no credit cost) before composing expensive scans

## Honest limitations

- **Schema drift**: Spellbook table names change. The templates here may need re-validation; treat them as starting points, not gospel.
- **Cross-chain query cost**: Querying 10 chains at once can hit slow-query timeouts even at 300s. For sector-wide scans, often better to run per-chain and aggregate client-side.
- **No real-time guarantee**: Dune indexes with a lag of minutes to hours depending on chain and table. Don't use for HFT.
- **No actual price feed for non-mainstream tokens**: Spellbook's `prices.usd` covers majors well, long-tail tokens may have gaps — output USD figures with caveats.
