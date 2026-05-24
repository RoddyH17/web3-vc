---
name: unit-economics
description: Web3 protocol unit economics analysis — fee generation, P/S ratio, fees/TVL, real user count, incentive vs organic activity, and capital efficiency. Translates traditional unit-economics frameworks (P/S, retention, take rate) to on-chain protocols. Uses the DefiLlama MCP connector for fundamentals. Use when evaluating a single protocol's economic quality, deciding whether TVL is "real", or comparing a protocol to its category peers. Triggers on "unit economics", "P/S ratio", "fees TVL", "real users", "is the TVL real", "protocol fundamentals", "capital efficiency".
---

# Web3 Protocol Unit Economics

This skill produces a **structured fundamentals sheet** for a single protocol — analogous to traditional PE unit economics, adapted for on-chain businesses. It does not output a buy / pass / hold opinion; it outputs the substrate the user makes that call on.

## Inputs

A protocol slug or name (`hyperliquid`, `uniswap`, `aave`, etc.). If ambiguous, use DefiLlama's `list_protocols` to surface candidates and ask the user to confirm the slug.

## Workflow

### Step 1: Identify protocol category and revenue model

Use `protocol_detail(slug)` to fetch metadata, then classify:

- **DEX / spot** — fees from swap volume × fee tier; competes on liquidity depth + UX
- **Perp DEX** — fees from notional volume × taker fee; competes on liquidity + leverage + UX
- **Lending** — interest rate spread between borrowers and lenders; fees = (borrow APR − supply APR) × utilization × TVL
- **Yield aggregator** — performance fee on user yield (typically 10–20%); revenue scales with underlying yield * AUM
- **LST / LRT** — staking commission on validator rewards (typically 5–10%)
- **Stablecoin issuer** — float income on reserves (USDC/USDT model) or stability fees (MakerDAO/Sky model)
- **Bridge / intent** — fees on transferred volume; competes on speed + cost
- **App-chain** — sequencer fees + MEV capture; competes on shared liquidity + custom execution

This classification determines which metrics matter. **Skip categories that don't apply** to keep the output focused.

### Step 2: Pull core fundamentals

Use DefiLlama tools:

| Metric | Tool | Notes |
|---|---|---|
| TVL (current + 30d + 1y) | `protocol_detail(slug)` | History array |
| Fees (24h, 7d, 30d) | `protocol_fees(slug)` | If protocol indexed by DefiLlama |
| Revenue (24h, 7d, 30d) | `protocol_fees(slug)` | Revenue = portion of fees accruing to protocol/token |
| Volume (DEX / perp only) | `protocol_volume(slug)` | |
| Token market cap / FDV | `protocol_detail(slug)` | For P/S calculation |
| Chains active on | `protocol_detail(slug)` | |

### Step 3: Compute unit economics

Compute these ratios — present each with the formula and the result:

| Ratio | Formula | Healthy range (heuristic) |
|---|---|---|
| **Fees / TVL (annualized)** | (fees_30d × 12) / TVL | DEX: >5%; lending: >2%; <1% = capital-inefficient |
| **P/S ratio** | FDV / (revenue_30d × 12) | <10x cheap, 10–30x reasonable, >50x rich |
| **P/F ratio** | FDV / (fees_30d × 12) | Useful when "revenue" is ambiguous (e.g., fees mostly go to LPs) |
| **Take rate** | revenue / fees | What share goes to the protocol vs LPs / users |
| **Revenue / TVL (annualized)** | (revenue_30d × 12) / TVL | <0.5% = poor monetization |
| **Volume / TVL (DEX only)** | volume_30d / TVL | Capital velocity; >5x/month = healthy |

Where data is missing (e.g., DefiLlama doesn't index fees for this protocol), say so explicitly — do not impute.

### Step 4: Real-user / quality checks

Mandatory red-flag screen:

- **Incentive intensity**: Does the protocol pay token emissions or points to LPs / users? If yes, estimate emissions value / fees ratio. If emissions > fees, organic demand is weak.
- **Concentration**: Is TVL dominated by 1–3 wallets? (For Phase 0, ask the user to manually check via a block explorer. Phase 1 will automate via Dune.)
- **Cross-chain double-counting**: For protocols on multiple chains, confirm DefiLlama is not double-counting bridged collateral.
- **TVL composition**: What assets make up the TVL? Heavy native-token collateral = reflexivity risk.

### Step 5: Peer comparison

Compare the target to its top 5 category peers (from `list_protocols(category=X, top_n=5)`):

| Metric | Target | Peer 1 | Peer 2 | Peer 3 | Peer 4 | Peer 5 |
|---|---|---|---|---|---|---|
| TVL | | | | | | |
| Fees 30d | | | | | | |
| Fees/TVL | | | | | | |
| P/S | | | | | | |
| 30d TVL Δ | | | | | | |

Highlight where the target is **>1 std dev** above or below the peer median.

### Step 6: Output format

Single markdown document:

```markdown
# {Protocol} Unit Economics — {Date}

## Classification
- Category: {category}
- Revenue model: {description}
- Chains: {list}

## Core fundamentals (pulled {timestamp})
- TVL: $XXm | 30d Δ: +/-Y%
- Fees 30d: $X.Xm | annualized: $YY.Ym
- Revenue 30d: $X.Xm | annualized: $YY.Ym
- FDV: $XXm | Market cap: $YYm

## Unit economics
{table from Step 3}

## Quality checks
- Emissions / fees: {ratio + interpretation}
- TVL composition: {breakdown}
- Concentration: {Phase 0 — flagged for user manual check / Phase 1 — Dune-driven}

## Peer comparison
{table from Step 5}

## Data provenance
- Source: DefiLlama API, pulled {timestamp}
- Missing data: {explicit list of metrics DefiLlama doesn't have for this protocol}
```

## Important Notes

- **No buy/pass/hold output.** This skill produces fundamentals. The investment call is the user's.
- **Flag missing data explicitly.** DefiLlama's coverage is uneven — some protocols have full fee indexing, some only TVL. Never impute; surface the gap.
- **Annualization caveat.** Multiplying 30d × 12 assumes stability. Add a note when activity is highly volatile (e.g., a meme coin launch).
- **FDV vs MC.** Default to FDV for P/S since token unlocks are real dilution. Show MC alongside so user can decide.
- **Save outputs.** Write to `./fundamentals/{protocol}-{YYYY-MM-DD}.md` for longitudinal tracking.

## Failure modes

- Protocol not on DefiLlama: stop, tell the user, suggest checking Token Terminal / Artemis manually.
- Fees not indexed: still produce TVL + market cap section; mark P/S as "unable to compute" and explain.
- Multi-chain protocol with inconsistent indexing: note which chains are covered and which are not.
