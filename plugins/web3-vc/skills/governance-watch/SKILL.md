---
name: governance-watch
description: "[Phase 1 stub] Tracks protocol governance proposals (Snapshot / Discourse) and GitHub commit activity for a configured watchlist of protocols. Surfaces leading indicators of protocol direction changes. Not yet implemented in Phase 0."
---

# Governance & Commit Watch (Phase 1 — NOT IMPLEMENTED)

## Status: STUB

This skill is scaffolded for design clarity but **not functional in Phase 0**. Invoking it will surface this notice.

## Phase 1 plan

### Connector dependencies
- **GitHub MCP** (official Anthropic / community version) — for commit activity, PR / issue stream
- **Discourse REST wrapper** — for governance forum proposals (e.g., gov.uniswap.org, forum.cow.fi, dydx.forum)
- **Snapshot GraphQL** — for on-chain governance vote data
- **Optional Phase 2**: Tally API for advanced governance analytics

### Watchlist config (planned)

User maintains a YAML watchlist at `./config/watchlist.yaml`:

```yaml
protocols:
  - name: uniswap
    github: Uniswap/v4-core
    governance_forum: https://gov.uniswap.org
    snapshot_space: uniswapgovernance.eth
  - name: hyperliquid
    github: hyperliquid-dex/contracts  # if/when public
    governance_forum: null  # currently no public forum
    snapshot_space: null
  - name: cow-protocol
    github: cowprotocol/contracts
    governance_forum: https://forum.cow.fi
    snapshot_space: cow.eth
```

### Workflow (planned)

1. Read `./config/watchlist.yaml`
2. For each protocol, in parallel:
   - GitHub: pull last 7d of commits to main branches; summarize subject lines; flag any PR with "audit", "migration", "v2", "breaking" in title
   - Governance forum: pull last 7d of new topics; summarize titles; flag any with high engagement (top 10% of forum)
   - Snapshot: pull active proposals; surface ones closing within 72h
3. Produce a weekly watchlist briefing:

```markdown
# Watchlist Briefing — {date}

## Uniswap
### GitHub (Uniswap/v4-core)
- 14 commits this week
- Notable: PR #1234 "Adds hook for X" — merged Tue
- Flag: PR #1245 mentions "migration" — needs review

### Governance (gov.uniswap.org)
- 3 new topics, 1 high-engagement: "Should we deploy on {new chain}?" — 47 replies

### Snapshot
- 1 active proposal: "Treasury diversification" — closes in 36h

## Hyperliquid
### GitHub
- Repository not public

### Governance
- No public forum
- (Watching X / Discord manually)

...
```

4. Write to `./watchlist/briefing-{YYYY-MM-DD}.md`

### Design intent

Governance forums and commit streams are the **most leading** indicators of protocol direction. By the time something is on Twitter, it's already been discussed for weeks in governance. This skill makes that signal accessible without manually checking 10 forums.

The output is intentionally **summary-only** — it surfaces what to look at, not what to conclude. The user clicks through to read the actual proposal.

## Triggers

"governance watch", "track proposals", "commit activity", "watchlist briefing", "what's changing in {protocol}"
