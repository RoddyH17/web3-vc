# web3-vc

A research plugin for Web3 venture capital — sector scanning, protocol unit economics, smart-money sourcing, and on-chain microstructure analysis. Built on the [Claude Code plugin architecture](https://docs.claude.com/), structurally modeled after [`anthropics/financial-services`](https://github.com/anthropics/financial-services) but oriented to crypto-native investing (DEX, perpetuals, intents, app-chains, RWA, liquid staking).

This is **not** a re-skin of the PE plugin. The skills here translate traditional analyst frameworks (deal sourcing, unit economics, IC memos) into on-chain equivalents that respect Web3's actual economic mechanics — fees-on-volume, oracle-priced TVL, incentive emissions, governance forums, and on-chain microstructure.

## Design philosophy

> **Human-led, AI-bounded.** This plugin amplifies a human researcher's workflow. It does not replace the conviction call.

Three guardrails are baked into every skill:

1. **Skills produce data substrate, not opinions.** `/sector` returns market structure. `/unit-economics` returns fundamentals. `/scout` returns candidates. The investment take is the user's.
2. **Falsifiers are first-class.** The (Phase 1) `/thesis` skill refuses to compose a thesis that doesn't include an explicit falsifier — what observation would prove it wrong.
3. **Data provenance is mandatory.** Every output records pull timestamps and source URLs. Stale data is surfaced, not hidden.

## What's in the plugin

Claude Code plugin skills are namespaced under the plugin name, so all commands are invoked as `/web3-vc:<command>`.

### Active (Phase 0)

| Command | Skill | Connector | Status |
| --- | --- | --- | --- |
| `/web3-vc:sector` | sector-scan | DefiLlama | ready |
| `/web3-vc:unit-economics` | unit-economics | DefiLlama | ready (light) |
| `/web3-vc:fundamental` | fundamental | DefiLlama + CoinGecko | ready (deep: bridge audit + Gordon reverse-engineering) |
| `/web3-vc:scout` | smart-money-scout | DefiLlama | ready (limited) |

### Scaffolded (Phase 1 — design only)

| Command | Skill | Connector needed | Status |
| --- | --- | --- | --- |
| `/web3-vc:onchain` | onchain-flow | Dune Analytics MCP | stub |
| `/web3-vc:thesis` | thesis-draft | (none new) | stub |
| `/web3-vc:watch` | governance-watch | GitHub MCP + Discourse REST | stub |

## Repository layout

This repo is a Claude Code **marketplace** containing one **plugin**. Claude Code requires this separation: a marketplace catalog at the root, with each plugin in its own subdirectory under `plugins/`.

```text
web3-vc/                                  # marketplace root
├── .claude-plugin/
│   └── marketplace.json                  # marketplace catalog (lists the plugin)
├── plugins/
│   └── web3-vc/                          # the plugin
│       ├── .claude-plugin/
│       │   └── plugin.json               # plugin manifest
│       ├── .mcp.json                     # connector wiring
│       ├── hooks/hooks.json              # (empty in Phase 0)
│       ├── commands/                     # slash-command entrypoints
│       │   ├── sector.md
│       │   ├── unit-economics.md
│       │   ├── scout.md
│       │   ├── onchain.md                # stub
│       │   ├── thesis.md                 # stub
│       │   └── watch.md                  # stub
│       ├── skills/                       # workflow + methodology
│       │   ├── sector-scan/SKILL.md
│       │   ├── unit-economics/SKILL.md
│       │   ├── smart-money-scout/SKILL.md
│       │   ├── onchain-flow/SKILL.md     # stub
│       │   ├── thesis-draft/SKILL.md     # stub
│       │   └── governance-watch/SKILL.md # stub
│       ├── connectors/
│       │   └── defillama/                # local Python MCP server
│       │       ├── pyproject.toml
│       │       ├── src/defillama_mcp/
│       │       └── tests/
│       └── CONTRIBUTING.md
├── README.md
├── LICENSE
└── .gitignore
```

## Install

### Prerequisites

- [Claude Code](https://docs.claude.com/) v2.1.150 or later — desktop / VS Code / CLI
- [`uv`](https://docs.astral.sh/uv/) — the DefiLlama MCP server is spawned via `uv run`
- Python 3.11+

### Step 1: Add the marketplace and install the plugin

In Claude Code, run:

```text
/plugin marketplace add RoddyH17/web3-vc
/plugin install web3-vc@web3-vc
```

The marketplace ships with one plugin (also named `web3-vc`), so the install syntax is `<plugin-name>@<marketplace-name>` — both happen to be `web3-vc`.

### Step 2: Verify

Type `/` in Claude Code and you should see commands under the `web3-vc:` namespace:

- `/web3-vc:sector`
- `/web3-vc:unit-economics`
- `/web3-vc:scout`
- (plus the Phase 1 stubs)

Verify the MCP connector is up:

```text
/mcp
```

You should see `defillama` listed and connected.

### Step 3: Smoke test

```text
/web3-vc:sector dexs
```

Returns the top 20 spot DEXes by 7-day volume.

### Connector dev (optional, for contributors)

If you're modifying the DefiLlama connector source, sync deps and run tests locally:

```bash
cd plugins/web3-vc/connectors/defillama
uv sync --extra dev
uv run pytest -xvs tests/
```

Six integration tests should pass (they hit the live DefiLlama API).

## Sample workflows

### Weekly DEX sector scan

```text
/web3-vc:sector dexs
/web3-vc:sector derivatives
```

Outputs are written to `./scans/{sector}-{date}.md` relative to the working directory.

### Deep-dive a protocol

```text
/web3-vc:unit-economics hyperliquid
```

Output written to `./fundamentals/hyperliquid-{date}.md`.

### Discover candidates aligned with a thesis

```text
/web3-vc:scout perp DEX next-gen microstructure
```

Output written to `./scout/{thesis-slug}-{date}.md`.

## Roadmap

### Phase 0 (this commit)

- DefiLlama connector
- 3 working skills (sector, unit-economics, scout)
- 3 Phase 1 skill scaffolds with design specs

### Phase 1 (next 2–3 weeks)

- Dune Analytics MCP (free tier)
- GitHub MCP (official)
- Discourse REST wrapper for governance forums
- `/onchain` skill wired with 7 curated SQL templates
- `/watch` skill wired
- `/thesis` skill — composition + stress-test layer

### Phase 2 (deferred, if/when justified)

- Token Terminal MCP (paid — only if budget justifies)
- Nansen / Arkham smart-money flows (paid)
- Snapshot GraphQL for governance vote data
- Messari Enterprise fundraising database

## Honest limitations

- **DefiLlama-only coverage.** Many sectors (AI agents on-chain, prediction markets, MEV infrastructure) are sparsely covered. The skills will surface these gaps explicitly.
- **Perpetual DEX volume aggregate is paywalled.** As of 2026-05, DefiLlama's `/overview/derivatives` returns 402 (Pro tier required). The `derivatives_overview` tool falls back to a TVL-ranked perp DEX list — still useful, but volume comparisons require per-protocol calls (`protocol_dex(slug)`).
- **No automated fundraising data in Phase 0.** Smart-money sourcing is half-manual until Phase 1 / 2 connectors land.
- **No on-chain microstructure in Phase 0.** Dune-driven LP / trader / MM analysis is a Phase 1 deliverable.
- **English-language sources only** for governance / commits in Phase 1 scope. Chinese-language Web3 sources (Foresight, Odaily, ChainCatcher) are out of scope for now.

### DefiLlama endpoint status (Phase 0)

| Endpoint | Used by tool | Status |
| --- | --- | --- |
| `/protocols` | `list_protocols`, `derivatives_overview` (fallback) | free |
| `/protocol/{slug}` | `protocol_detail` | free |
| `/v2/chains` | `list_chains` | free |
| `/overview/dexs` | `dex_overview` | free |
| `/overview/derivatives` | `derivatives_overview` (primary) | Pro tier (402) — fallback active |
| `/overview/fees` | `fees_overview` | free |
| `/summary/fees/{slug}` | `protocol_fees` | free |
| `/summary/dexs/{slug}` | `protocol_dex` | free |

## Relationship to upstream

This plugin is structurally inspired by `anthropics/financial-services` but is a standalone repository, not a fork. The directory layout, manifest format, and skill+command pattern follow the upstream conventions so future plugins from either side stay interoperable.

It is **not endorsed by Anthropic** and makes no claim to be official.

## License

MIT. See `LICENSE`.

## Disclaimer

Nothing in this repository constitutes investment, legal, tax, or accounting advice. The skills draft analyst work product for review by a qualified professional. They do not make investment recommendations, execute transactions, or commit capital. Every output is staged for human review.
