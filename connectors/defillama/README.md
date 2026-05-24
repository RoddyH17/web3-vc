# DefiLlama MCP Connector

MCP server wrapping the free, public DefiLlama API. Powers the `sector-scan`, `unit-economics`, and `smart-money-scout` skills of the `web3-vc` plugin.

## Why DefiLlama

- Free, no API key
- Broadest cross-chain TVL / volume / fees coverage in the industry
- Authoritative sector dominance numbers
- Stable schema

## Setup

This connector uses [`uv`](https://docs.astral.sh/uv/) for environment management. Install uv if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then sync deps from this directory:

```bash
cd connectors/defillama
uv sync
```

## Run the server standalone (for debugging)

```bash
uv run python -m defillama_mcp.server
```

The server speaks the MCP stdio protocol. In normal use you don't invoke it directly — Claude Code spawns it via the plugin's `.mcp.json`.

## Run tests

```bash
uv run pytest -xvs tests/
```

Tests hit the live DefiLlama API (marked `@pytest.mark.integration`). To skip:

```bash
uv run pytest -m "not integration"
```

## Available tools

| Tool | Purpose |
|---|---|
| `list_protocols(category?, chain?, top_n=20)` | Top protocols by TVL, filterable |
| `protocol_detail(slug)` | Full data for one protocol |
| `protocol_fees(slug)` | 24h/7d/30d fees + revenue for one protocol |
| `dex_overview(top_n=20)` | Spot DEX leaderboard by 7d volume |
| `derivatives_overview(top_n=20)` | Perp DEX leaderboard by 7d volume |
| `fees_overview(top_n=20)` | Top fee-generating protocols across all categories |
| `list_chains(top_n=20)` | Top chains by TVL |

## DefiLlama category names (case-sensitive)

Common ones the skills use:

- `Dexs` (spot DEXes)
- `Derivatives` (perpetual / options DEXes)
- `Lending`
- `Yield`
- `RWA`
- `Liquid Staking`
- `Liquid Restaking`
- `Bridge`
- `CDP`

If a filter returns empty, check the exact spelling at https://defillama.com/categories.

## Rate limiting

DefiLlama is generous but not unlimited. The skills generally make 1–3 calls per invocation. Avoid running scans in tight loops.
