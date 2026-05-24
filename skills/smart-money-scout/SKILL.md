---
name: smart-money-scout
description: Web3 project discovery workflow — surfaces candidate projects via sector momentum (DefiLlama) and fundraising signals, cross-referenced against the user's investment thesis. Phase 0 uses DefiLlama only; Phase 1 will add Nansen / Arkham smart-money flows. Use when asked to "find new projects", "scout deals", "what's getting traction", "anomaly hunt", or "candidate list". Triggers on "scout", "discover projects", "deal sourcing", "new entrants", "smart money", "anomaly hunt".
---

# Smart-Money Scout (Phase 0 — Momentum + Fundraising)

This skill surfaces candidate projects the user should look at. It does **not** rank them by quality or make an invest/pass call — it produces a structured candidate list with rationale, so the user can decide where to spend deeper diligence time.

## Phase status

- **Phase 0 (current)**: DefiLlama-driven momentum scan + manual user prompts for fundraising context.
- **Phase 1 (planned)**: Nansen Smart Money flows + Arkham entity tracking + Messari fundraising database.
- **Phase 2 (planned)**: Custom Dune queries for whale-cohort behavior, recurring smart-money buyers, etc.

When running this skill, always state which phase is active so the user knows the limitations.

## Inputs

Either:
- A thesis statement or sector hint (`"perp DEX next-gen microstructure"`, `"intent-based aggregators"`, `"AI agents on-chain"`)
- Or no input — in which case ask the user for their current thesis before scanning. Scouting without a thesis produces noise, not signal.

## Workflow

### Step 1: Translate thesis to DefiLlama categories

Map the user's thesis to one or more DefiLlama categories. Examples:

| Thesis | DefiLlama categories to scan |
|---|---|
| Perp DEX next-gen microstructure | `derivatives` |
| Intent-based DEX | `dexs` (filter for projects tagged "intent" / "aggregator" / "RFQ") |
| RWA tokenization | `rwa` |
| Liquid staking innovation | `liquid staking`, `liquid restaking` |
| AI agents on-chain | (Phase 0 limitation — DefiLlama doesn't have this category; surface as gap) |

If the thesis doesn't map cleanly, ask the user to refine or pick the closest analog.

### Step 2: Run momentum scan

For each mapped category:

- `list_protocols(category=X, top_n=50)` — get top 50 by TVL
- Compute 30-day rank change for each protocol (current rank vs estimated rank 30d ago, derivable from TVL history)
- Flag protocols that meet **any** of these criteria:
  - **Top-of-category newcomer**: entered top 20 within the past 30d
  - **Velocity**: TVL_change_30d > +50%
  - **Volume divergence**: volume_30d_change > 2× TVL_30d_change (signals real usage outpacing capital)
  - **Fee divergence**: fees_30d_change > 2× TVL_30d_change (signals monetization outpacing capital)
  - **New listing**: protocol added to DefiLlama within past 60d AND TVL > $10m

### Step 3: Filter for relevance

For each flagged protocol, fetch `protocol_detail(slug)` and check:

- Does the protocol's description / tags align with the thesis?
- Is the team / chain / launch date plausibly relevant?

Drop irrelevant matches. The output of this step should be 5–15 protocols, not 50.

### Step 4: Fundraising context (Phase 0: manual prompt)

For each surviving candidate, ask the user:

- "Do you recall a recent fundraise for {protocol}?"
- "Have you seen any specific VCs you respect investing in this space recently?"

In Phase 1, this step will be automated via Messari Enterprise / Crunchbase API.

### Step 5: Output format

```markdown
# Scout Candidates — {thesis} — {date}

## Phase: 0 (DefiLlama momentum + user-provided fundraising context)

## Candidates

### 1. {Protocol Name}
- **Why flagged**: {one or more momentum criteria from Step 2}
- **TVL**: $XXm | 30d Δ: +Y%
- **Volume 30d**: $XXm | 30d Δ: +Z%
- **Fees 30d**: $X.Xm | 30d Δ: +W%
- **Chains**: {list}
- **Thesis fit**: {1-2 sentence rationale for relevance}
- **Fundraising**: {user-provided, or "Unknown — recommend manual check on Messari Enterprise"}
- **Next step**: Run `/unit-economics {slug}` for fundamentals.

### 2. {Protocol Name}
...

## Gaps (couldn't scout from DefiLlama alone)
- {e.g., "AI agents on-chain doesn't map to a DefiLlama category — recommend manual scan of Twitter + a16z / Variant portfolios"}
- {e.g., "Permissioned / institutional DeFi often not indexed — manual"}

## Data provenance
- DefiLlama, pulled {timestamp}
- Fundraising info: user-provided ({Phase 0 limitation})
```

## Important Notes

- **Quality over quantity.** Better to surface 5 well-screened candidates than 30 noisy ones. The user's time is the bottleneck, not your search breadth.
- **Always state phase limitations.** The user needs to know what signal you didn't get from this scan. List gaps explicitly so they don't assume false comprehensiveness.
- **Don't rank by "best".** Rank by momentum criterion strength, not by quality judgment. Quality is downstream — that's `/unit-economics` and the user's own thesis work.
- **Save outputs.** Write to `./scout/{thesis-slug}-{YYYY-MM-DD}.md` so the user can compare scouts across weeks and see which candidates keep recurring (a meta-signal in itself).

## Failure modes

- Thesis too vague: ask for a more specific sector / mechanism / market segment before scanning.
- All flagged protocols are obvious top names: lower the rank threshold in Step 2 (look at top 100 instead of top 50) — the goal is to surface non-obvious candidates.
- No candidates pass relevance filter: report this honestly. "DefiLlama-indexed protocols don't currently match this thesis." Suggest the user manually scan Twitter or talk to founders directly.
