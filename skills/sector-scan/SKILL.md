---
name: sector-scan
description: Web3 sector scanning workflow — produces a structured weekly briefing on TVL, volume, fees, and dominance shifts for a specified sector (DEX, perpetuals, lending, RWA, yield) or chain. Uses the DefiLlama MCP connector. Use when asked to "scan a sector", "weekly DeFi briefing", "what's happening in perps / DEX / lending", or "find sector anomalies". Triggers on "sector scan", "weekly briefing", "TVL changes", "dominance shifts", "DEX volume", "perp volume", "fee leaders", "chain activity".
---

# Web3 Sector Scan

This skill produces a **structured, data-only briefing** for a Web3 sector. It does **not** form investment opinions — the user's thesis layer is separate. The output is the raw signal substrate the user reasons over.

## Inputs

The user provides a sector identifier, one of:

- `dexs` — spot DEX volume + TVL
- `derivatives` — perpetual / options DEX volume + OI
- `lending` — money market protocols
- `rwa` — real-world asset tokenization
- `yield` — yield aggregators / vaults
- `stablecoins` — stablecoin supply + dominance
- A chain name (`ethereum`, `solana`, `base`, `hyperliquid`, `arbitrum`, etc.) — produces a chain-level scan

If the user input is ambiguous (e.g. "DeFi"), ask which sector specifically.

## Workflow

### Step 1: Pull current snapshot

Use the DefiLlama MCP connector tools:

- For protocol-level sectors (`dexs`, `derivatives`, `lending`, `yield`):
  - `list_protocols(category=<Sector>, top_n=20)` for top 20 by TVL — note DefiLlama capitalization (`Dexs`, `Derivatives`, `Lending`, `Yield`, `RWA`, `Liquid Staking`)
  - `dex_overview()` for spot DEX volume aggregate (free)
  - `derivatives_overview()` for perp DEX — **note: the volume endpoint is currently Pro-tier; the tool falls back to a TVL-ranked perp DEX list, which is still useful but volume comparisons must be made via `protocol_dex(slug)` per protocol**
  - `fees_overview()` for fees / revenue across all categories

- For `rwa` / `stablecoins`:
  - `list_protocols(category=<sector>, top_n=15)`
  - `stablecoin_overview()` for stablecoin-specific data (when sector=stablecoins)

- For chain-level scans:
  - `list_chains(top_n=15)` to confirm the chain ranks
  - `list_protocols(chain=<chain>, top_n=15)` for top protocols on that chain

### Step 2: Compute deltas

For each protocol in the top 20, compute:

| Metric | Window | Source |
|---|---|---|
| TVL change | 1d, 7d, 30d | `list_protocols` returns `change_1d`, `change_7d`, `change_1m` |
| Volume change | 7d vs prior 7d | `dex_overview` |
| Fees change | 7d vs prior 7d | `fees_overview` |
| Dominance shift | sector market share, 7d delta | derived from sum of category TVL |

### Step 3: Flag anomalies

Emit a separate "Anomaly" section flagging:

- Any protocol with **|TVL change_7d| > 20%**
- Any protocol with **volume_7d change > 30%** (up or down)
- Any new entrant into top 10 by TVL or volume within the past 30 days
- Any dominance shift > 3 percentage points week-over-week within the sector

For each anomaly, do **not** speculate why — just record:
- The metric and magnitude
- Protocol name + URL
- One-line context if obvious from DefiLlama metadata (e.g., "TVL drop coincides with stETH unwind period")

### Step 4: Cross-sector context

Include a brief "Cross-sector context" block:

- Total sector TVL change vs total DeFi TVL change (is the sector outperforming?)
- For derivatives: ratio of perp DEX volume to spot DEX volume (a microstructure signal)
- For DEX: ratio of DEX volume to CEX volume estimate (DefiLlama provides DEX share)

### Step 5: Output format

Produce a single Markdown document with this structure:

```markdown
# {Sector} Sector Scan — {Date}

## Top 20 Snapshot
| Rank | Protocol | TVL | 7d Δ | 30d Δ | Chains |
|---|---|---|---|---|---|
...

## Volume Leaders (7d)
| Rank | Protocol | Volume 7d | WoW Δ | Fees 7d |
|---|---|---|---|---|
...

## Anomalies
- [Protocol]: TVL down 28% in 7d. URL.
- [Protocol]: New entrant — moved from rank 25 → 8 in 30d. URL.
...

## Cross-sector context
- Sector TVL: $XX.Xb (Y% WoW); total DeFi: $ZZ.Zb (W% WoW); sector relative: +/-N pp
- {sector-specific ratios}

## Data provenance
- Source: DefiLlama API, pulled {timestamp}
- Categories scanned: {list}
- Snapshot is point-in-time; does not reflect intraday moves
```

## Important Notes

- **No opinions in this skill.** The output is signal substrate, not analysis. Investment commentary lives in `thesis-draft`.
- **No speculation about causes.** If a protocol TVL dropped 30%, record the fact. Do not write "this is probably because X" unless X is documented in the DefiLlama metadata or the user explicitly asked for hypothesis generation.
- **TVL is gameable.** Always cross-reference with fees and volume — a protocol with high TVL but no fees / no volume is usually recursive lending or self-incentivized.
- **Time-stamp everything.** DefiLlama numbers shift hour to hour. Always record the pull timestamp in the output.
- **Stable sort.** When ranking, break ties by protocol name alphabetically so weekly briefings are diff-able.
- **Save outputs.** Write the markdown to `./scans/{sector}-{YYYY-MM-DD}.md` so the user can build a longitudinal record. If `./scans/` doesn't exist, create it.

## Failure modes to handle

- DefiLlama API rate-limited or 5xx: retry once with 2s backoff, then surface the error and tell the user to retry in 5 min. Do not silently fall back to stale data.
- Sector returns empty: confirm the category name with the user — DefiLlama category names are specific (`dexs` not `dex`, `derivatives` not `perps`).
- User asks for a chain not indexed by DefiLlama: list the supported chains via `list_chains()` and ask user to pick.
