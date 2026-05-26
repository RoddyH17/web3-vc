# Web3 Metrics & Signals — A Researcher's Reference

This document is the analytical layer that sits underneath the `/web3-vc:sector`, `/web3-vc:unit-economics`, and `/web3-vc:scout` commands. The skills produce data; this document explains **what the data means**, **what reading patterns matter**, and **what next step each pattern should trigger**.

It is opinionated about methodology, agnostic about specific investments. Every recommendation here is structural ("when you see X, look at Y") — never directional ("X is bullish").

## Why we measure at all

A Web3 protocol is a **fee-generating machine sitting on top of locked capital**. The investment question is always some variant of:

1. **Is the fee stream real?** (vs. wash-traded / sybil-driven / incentive-bought)
2. **Is it growing for the right reasons?** (organic demand vs. emissions vs. point-farming)
3. **Is it durable?** (defensible moat vs. mercenary capital that leaves with the next program)
4. **Is the capital being used efficiently?** (high fees per dollar of TVL = better business)
5. **How is value flowing to the token?** (take rate, buybacks, accrual mechanics)

Every metric below is a probe into one of these five questions. If you find yourself collecting a metric that doesn't map to one of them, drop it — it's vanity.

---

## Part 1: Foundational metrics

### 1.1 TVL (Total Value Locked)

**Definition.** The dollar-denominated sum of all assets sitting in a protocol's smart contracts at a point in time.

**What it actually measures.** Capital deposited — which is a *necessary but not sufficient* condition for revenue generation. TVL is the "raw material" a protocol works with.

**What it does NOT measure.**

- **Usage.** A pool with $1B TVL and zero swaps generates zero fees.
- **Quality of capital.** $1B in stablecoins behaves differently from $1B in a governance token.
- **Net new capital.** TVL can rise from price appreciation of underlying assets, not new deposits.

**How TVL can be misleading (the four common games).**

1. **Recursive borrowing / leverage looping.** User deposits $100, borrows $80, redeposits $80, borrows $64, redeposits... TVL inflates to ~$500 from $100 of "real" capital.
2. **Native-token collateral.** A protocol whose TVL is 80% its own governance token has reflexive TVL — token price drops 50%, TVL drops 50%, without any user leaving.
3. **Bridged double-counting.** Some sources count the same ETH twice (once on L1, once on L2 after bridging). DefiLlama generally handles this but edge cases exist.
4. **Liquidity mining inflated.** Capital that flows in for a points / emissions program and leaves the moment the program ends. The TVL is "real" while present but mercenary.

**How to read TVL correctly.**

| Pattern | Interpretation |
| --- | --- |
| TVL up + fees up proportionally | Healthy growth — more capital is being put to work |
| TVL up + fees flat | Mercenary capital arriving; probably incentive-driven |
| TVL flat + fees up | Existing capital working harder; usually positive (productivity) |
| TVL up + token price up by same % | Largely reflexive; check the composition |
| TVL up + price down | Strong signal — actual new deposits despite headwinds |

### 1.2 Volume

**Definition.** Notional value of transactions routed through the protocol over a window (24h, 7d, 30d). For DEXes: swap volume. For perp DEXes: notional traded volume. For bridges: bridged value.

**What it actually measures.** Demand for the protocol's primary service. Less gameable than TVL because volume requires actual transactions (each costing gas).

**What it does NOT capture.**

- **Quality of flow.** Wash trading is real, especially for protocols running points programs. Solana DEXes saw documented wash trading 2024–2025.
- **Profitability per dollar of volume.** Different fee tiers mean a DEX doing $1B vol at 0.05% fees makes less than another doing $500m at 0.3%.
- **Concentration.** $1B from 1 wallet ≠ $1B from 100,000 wallets.

**How to read volume.**

- **Volume growing faster than TVL** = capital efficiency improving (the protocol is doing more with less). This is one of the strongest positive signals.
- **Volume falling while TVL stable** = capital getting trapped. Check why users aren't transacting.
- **Volume spiking then crashing** = often a launch/incentive event. Look at the trailing 30d, not the spike.

### 1.3 Fees and Revenue

These are different and people confuse them constantly.

**Fees** = total dollar amount collected from users for using the protocol. This pool is then split — some to LPs, some to the protocol/token, some to other stakeholders.

**Revenue** = the portion of fees that accrues to the protocol or token holders specifically. Sometimes called "protocol revenue" or "supply-side revenue".

**Take rate** = `revenue / fees`. The percentage the protocol/token captures.

**Why the distinction matters.**

- Uniswap V3 charges 0.3% (or other tiers). Of that, **100% goes to LPs**, 0% to UNI holders (under the current fee switch state). So Uniswap has billions in fees but ~$0 revenue.
- Aave's interest rate spread is fees; the reserve factor portion is revenue.
- GMX historically had a ~30% take rate (LPs got 70% via GLP, protocol got 30%).

**For unit economics analysis, always use revenue.** For relative attractiveness across competitors, fees is fine (because LPs care about fees as their yield).

### 1.4 Market Cap and FDV

- **Market Cap** = current circulating supply × token price.
- **FDV (Fully Diluted Valuation)** = max supply × token price.

**For DeFi, default to FDV.** Token unlocks are real and material. A protocol with $200m MC but $2b FDV will see 10× dilution as tokens vest, which is the same as a 90% price drop for current holders at constant FDV.

**Exception:** for memecoins or tokens with 100% circulating, MC = FDV and it doesn't matter.

---

## Part 2: Derived ratios — the capital efficiency framework

These are the workhorses of unit economics for Web3. Each tells you something specific.

### 2.1 Fees / TVL (annualized)

**Formula:** `(fees_30d × 12) / current_TVL`

**What it tells you:** how productive each dollar of locked capital is. Equivalent to asking "what APR is this protocol generating for its LPs / suppliers / participants, before token incentives?"

**Reference ranges (rules of thumb, sector-specific):**

| Sector | Healthy | Mediocre | Concerning |
| --- | --- | --- | --- |
| Spot DEX (AMM) | >15% | 5–15% | <5% |
| Perp DEX (oracle-based, e.g. GMX) | >25% | 10–25% | <10% |
| Perp DEX (orderbook, e.g. dYdX, Hyperliquid) | >100% | 50–100% | <50% |
| Lending | >5% | 2–5% | <2% |
| LST (commission base) | >0.5% | 0.2–0.5% | <0.2% |
| Yield aggregator | >5% (of underlying TVL) | 2–5% | <2% |

Perp DEXes have far higher ratios because LP capital is collateral against leveraged positions — the same $1 backs 10×–20× the notional volume. This is not anomaly; it's the model.

**Common traps:**

- Bull market spikes — fee/TVL was much higher in Q1 2024 for everyone. Use a longer window or compare relative to peers in the same period.
- Promo periods — fees can spike during an incentive program if users transact more aggressively to farm points.

### 2.2 Volume / TVL (capital velocity)

**Formula:** `volume_30d / current_TVL`

**What it tells you:** how many times the locked capital "turns over" in a month. A capital velocity proxy. Useful primarily for DEX/perp.

**Reference ranges (DEX-specific):**

- **Spot AMM (Uniswap V2 / Sushi / Pancake)**: 1–5x/month is typical. Concentrated liquidity (V3) can hit 20–100x because LPs concentrate in narrow ranges.
- **Curve-style stableswap**: usually low (0.5–3x) because narrow spreads mean low volume per dollar — but combined with low IL, can still be profitable.
- **Perp DEX**: 5–50x/month for oracle-based; orderbook DEXes can exceed 200x (notional volume on margin).

**How to read it:**

- **High volume/TVL with low fees/TVL** = razor-thin margins, possibly wash trading. Investigate.
- **Rising volume/TVL** over time = the protocol's LPs are becoming more efficient. Almost always good.
- **Falling volume/TVL** while volume stable = TVL piling up. Look at JIT (just-in-time) bot activity capturing fills.

### 2.3 Revenue / TVL (monetization)

**Formula:** `(revenue_30d × 12) / current_TVL`

**What it tells you:** how well the *token holders* are paid for the capital sitting in the protocol. The "real" returns to token economics.

- Below 0.5%: very poor monetization. Token holders earn almost nothing per dollar of TVL.
- 0.5–3%: average for DeFi blue chips.
- >3%: strong monetization (usually means high take rate + healthy fees).

### 2.4 Take rate

**Formula:** `revenue / fees`

| Take rate | Typical use case |
| --- | --- |
| 0% | Pure LP-funded (Uniswap V3 default) |
| 5–15% | Moderate protocol fee (Maker stability fee, Aave reserves) |
| 20–40% | Aggressive (GMX, dYdX historical) |
| >50% | Effectively a closed-source rent-seeking position — sustainable only with strong moats |

**Trap:** A high take rate is great for the token until competitors with lower take rates emerge. Pendle's success against Convex stack shows how this dynamic plays out.

### 2.5 P/S and P/F (valuation multiples)

**P/S = FDV / (revenue_30d × 12)**
**P/F = FDV / (fees_30d × 12)**

**Reference ranges (Web3, very rough):**

| Multiple | What it implies |
| --- | --- |
| <5x P/S | Deep value (or dying — check growth) |
| 5–15x P/S | Mature blue chip pricing (analogous to mature fintech) |
| 15–40x P/S | Growth pricing |
| 40–100x P/S | High growth or speculative |
| >100x P/S | Memecoin / pre-revenue / vapor |

**Critical caveat:** Web3 P/S is much noisier than equity P/S because:
- Revenue can be inflated by short-lived incentives
- FDV moves on speculative cycles unrelated to fundamentals
- Token does not always have full claim on protocol cash flows

Use P/S as **one** sanity-check, never as the sole valuation input.

---

## Part 3: Quality screens (red flag checklist)

Before trusting any of the ratios above, run these screens on the protocol:

### 3.1 Organic vs incentive

**Question:** what fraction of activity exists because of native demand vs. because of token emissions or points?

**Heuristics:**

- Token emission rate (annualized $ value of incentives) vs. fees generated. If emissions > fees, the protocol is paying users more than they're paying it. Mercenary.
- Look at activity in the 30 days *after* a points program ends. If TVL drops 60%, it was mercenary.
- Check whether other "incentive farmers" wallets (labeled by Nansen / Arkham — Phase 2) make up >30% of volume.

### 3.2 Concentration

**Question:** is the protocol dominated by a handful of wallets?

**Heuristics:**

- Top-10 LP share of TVL. Healthy <60%, concerning >80%.
- Top-10 trader share of volume. Same thresholds.
- For lending: top-3 borrowers. If one borrower is 40% of borrows, you have counter-party risk dressed up as a market.

### 3.3 TVL composition

**Question:** what kind of capital is sitting here?

**Categories to break down:**

- **Stablecoins**: most "real" — held by users for utility, sticky.
- **Blue-chip volatile (ETH, BTC)**: moderately real — speculatively held but liquid and large.
- **Native governance token**: reflexive — TVL moves with token price, not user behavior.
- **Other tokens**: case-by-case.

Run this check via `protocol_detail(slug)` — the `currentChainTvls` breakdown often segments by category.

### 3.4 Cross-chain double counting

**Question:** is the same dollar counted twice?

Most relevant for protocols deployed on multiple L2s sharing bridged collateral. DefiLlama generally deduplicates but it's worth a sanity check by adding up the per-chain breakdowns and confirming they match the headline TVL.

### 3.5 Fee adapter coverage

**Question:** does DefiLlama actually have a fee adapter for this protocol?

If `protocol_fees(slug)` returns "not indexed", you cannot do P/S analysis from DefiLlama alone — fall back to Token Terminal (paid), or read the protocol's own dashboard, or compute manually from on-chain events. **Surface this gap explicitly**; don't impute.

---

## Part 4: Sector-specific microstructure

The metrics above are the universal framework. Each sector has specific dynamics that need additional signals.

### 4.1 Spot DEX (AMM-based)

**Additional signals to watch:**

- **Bid-ask spread (effective):** roughly the fee tier for AMMs. V3 0.05% tier vs 0.3% tier matters enormously for which pairs route there.
- **JIT capture:** what % of large fills are captured by just-in-time bots placing super-narrow liquidity for a single block? On Uniswap V3, this is reportedly 20–40% of large-trade fees on big pairs. JIT capture means retail LPs get less than the headline fee APR.
- **Routing dominance:** is this DEX in the default route of major aggregators (1inch, Matcha, Jupiter)? If not, it's invisible to most flow.

### 4.2 Perp DEX (oracle-based, GMX-style)

**Additional signals:**

- **GLP-style pool composition.** Multi-asset pools have asymmetric risk — heavy in stablecoins means more conservative, heavy in BTC/ETH means more exposed.
- **Skew (long vs short OI).** Persistent one-sided skew means LPs are taking concentrated exposure. Bad days for the asset = bad days for LPs.
- **Funding payments.** Who's paying whom, and at what rate. Heavily positive funding = longs paying shorts = market bullish but probably late.

### 4.3 Perp DEX (orderbook-based, Hyperliquid / dYdX-style)

**Additional signals:**

- **MM concentration.** How many designated MMs are providing liquidity? Top-3 share of fills?
- **Liquidation cascades.** Frequency and severity. A perp DEX with weekly cascades is structurally fragile.
- **Latency / block time.** Hyperliquid's ~70ms block time vs dYdX's ~1s vs others. Latency affects MM willingness to quote tight spreads.
- **Open Interest / Volume ratio.** Low OI/Volume = lots of in-and-out trading (scalpers, possible wash). High OI/Volume = positions are held.
- **Token-incentive intensity.** Most perp DEXes are running points programs in 2025–2026. Estimate the points-as-USD-equivalent run rate against fees generated. If points are >50% of fees, retention post-airdrop is the entire question.

### 4.4 Lending

**Additional signals:**

- **Utilization** = borrowed / supplied. 60–80% is the sweet spot. <40% = excess capital not being used. >90% = liquidity stress; lenders may not be able to withdraw.
- **Supply / borrow APR spread.** The protocol's effective gross margin. If spread is <50bps the protocol has no pricing power.
- **Bad debt ratio** = bad debt / total borrows. Should be ~0. Anything >0.5% is a sign of risk management failures (Euler 2023 was extreme).
- **Cross-asset isolation.** Pooled risk (Aave) vs. isolated markets (Morpho, Silo). Different risk profiles, different revenue models.

### 4.5 LST / LRT (Liquid Staking / Restaking)

**Additional signals:**

- **Commission rate.** Lido 10%, RocketPool 14% effective, Frax tBTC 8%. Higher commission = more revenue but invites lower-commission competitors.
- **Validator concentration.** Lido stETH is ~30% of ETH staked — protocol-level risk if it grows further.
- **Peg deviation.** stETH / ETH should track ~1.0. Deviations indicate redemption stress or speculative flows.
- **Restaking points / EigenLayer integration.** Phase-dependent — the value depends on the eventual restaking yield, which is still being discovered.

### 4.6 Bridge / Intent

**Additional signals:**

- **Time-to-finality.** Across promises seconds, others take 7+ days for optimistic withdrawals. Latency = competitive feature.
- **Solver concentration (intent-based).** On CoW Protocol, the top-3 solvers historically captured >70% of fills. If this stays high, solvers extract more rents and "competitive auction" becomes a misnomer.
- **Coverage breadth.** Number of supported chains × asset pairs. Often 80% of volume goes through 5% of routes.

### 4.7 Agentic trading on DEX (emerging category)

There's not yet a clean DefiLlama category for this, but as your research focus, here are the metrics that will eventually matter:

- **API surface and reliability.** Can an agent execute via REST / WebSocket / direct contract calls? Uptime SLAs?
- **Order types supported.** Market, limit, stop, OCO. Agents need expressive primitives.
- **Latency from intent to confirmation.** Block time is the floor; protocol-side queuing adds to it.
- **Slippage tolerance enforcement.** Predictable execution is more important than best-price execution for agents.
- **Account abstraction support.** Whether agents can run as ERC-4337 accounts with custom validators.
- **MEV protection** (sandwich resistance, private mempool routing). Agents that get sandwich-attacked underperform deterministically.

This is the area where DefiLlama provides the **least** signal in Phase 0 — most of these metrics need manual investigation, founder conversations, and direct testing. Flag it as a gap.

---

## Part 5: The Signal Grid — pattern → interpretation → next step

This is the operational table the workflow runs on. When the `/web3-vc:sector` or `/web3-vc:unit-economics` scan returns data, find the row that matches the pattern and execute the next step.

| Observed pattern | Most likely interpretation | Next analytical step |
| --- | --- | --- |
| TVL up 50% in 7d, fees flat | New incentive / points program attracted mercenary capital | Check token emission run-rate; check whether protocol just announced a points program; flag for re-scan in 30d |
| TVL flat, fees up 30% in 7d | Existing capital getting more productive (volatility spike or new feature) | Check 7d volume — if also up, it's organic; if not, fees may be one-off (liquidation cascade etc.) |
| TVL down 20%, fees down 5% | Capital leaving but transactional users staying | Check whether emissions just ended; check competitor TVL flows (capital often moves laterally) |
| TVL down 20%, fees down 50% | Both capital and demand leaving | Bearish signal. Run `/web3-vc:unit-economics` to see if P/S is still rich (downside not priced in) |
| Volume / TVL ratio rising (capital velocity up) | Capital is becoming more efficient — usually positive | Check whether this is JIT bot capture (extractive) or genuine LP improvement; on V3 DEXes, distinguish via Dune query (Phase 1) |
| Volume / TVL ratio falling (capital velocity down) | Capital is piling up but not being used | Check if a competing aggregator just changed routing; check whether the protocol just got delisted from a major venue |
| Fees / TVL annualized >50% on a non-perp protocol | Either wash trading or a temporary anomaly | Cross-check with on-chain unique addresses (Phase 1 Dune); if real, this is a top-quartile protocol |
| Take rate >40% with rising fees | Strong pricing power, but invites competition | Map the competitive landscape — who could undercut and how soon |
| Take rate 0% with very high fees (e.g., Uniswap) | LPs get all the upside; token holders speculate on future fee switch | Investment thesis must price the fee-switch governance probability |
| P/S < 5x with growing fees | Potential value play OR market knows something | Check the bear case — is regulatory risk pending? Is a fork imminent? |
| P/S > 50x with stable fees | Speculation dominant — narrative-driven | Don't anchor to P/S; price reflects expected category leadership not current economics |
| Emissions / fees > 1 | Protocol is paying users more than they pay it | Mercenary phase — note the emission schedule's end date; re-evaluate post-program |
| Top-10 LP share > 80% of TVL | Concentrated capital — single-actor risk | Identify the top LPs (Phase 2 Nansen); is this a single fund? A market maker? |
| Top-3 traders > 50% of volume | Wash trading suspicion, or single MM dominance | If perp DEX, this is normal (MMs dominate). If spot DEX, investigate. |
| TVL composition >50% native governance token | Reflexive TVL; correlated to token price | Discount headline TVL by ~50% mentally for any analysis |
| Multi-chain TVL split — single chain >80% | Effectively a single-chain protocol pretending otherwise | Run analysis on the dominant chain only |
| New protocol entered top 10 in <60 days | Strong momentum signal, but verify it's not points-driven | Run `/web3-vc:unit-economics` immediately; check whether founders are doxxed / has audit; check on-chain age of contracts |
| Volume falling but spread / fee tier mix shifting up | Users routing through higher-fee paths (deeper liquidity scarce) | Bearish on the protocol's pricing power but bullish on remaining LPs' profitability |
| Funding rate persistently >0.05% / 8h on a perp DEX | Bullish positioning is crowded | If you have a contrarian thesis, this is supporting evidence; if not, expect a long-side liquidation event |
| Open Interest dropping while volume stable on perp | Position holders are exiting; rotation period | Often precedes a directional move (in either direction) — don't read direction from this alone |

---

## Part 6: Common traps and what to ignore

Things that look like signal but mostly aren't:

1. **24h numbers.** Too noisy. Always anchor to 7d minimum, prefer 30d.
2. **Headline TVL of multi-chain protocols.** Always break down by chain — the dynamics differ wildly.
3. **Year-on-year comparisons.** Web3 markets rotate every 6 months. Apples-to-apples requires same market regime (bull, bear, sideways).
4. **"TVL ATH" announcements.** Often coincides with token price ATH and tells you nothing about productive capital.
5. **Twitter sentiment of users / token holders.** Inverse signal more often than not (bag-talkers).
6. **Founder Twitter follower counts / podcast appearances.** Vanity. Look at GitHub commit cadence and governance forum substance instead.
7. **Single-data-point comparisons across protocols of different ages.** A 6-month-old protocol vs. 4-year-old protocol have totally different baseline dynamics.

---

## Part 7: Workflow integration — when to use what

| When you want to... | Use this skill | What this doc tells you to read |
| --- | --- | --- |
| Get a top-down view of an entire sector | `/web3-vc:sector <vertical>` | Part 1 (foundational) + Part 5 (Signal Grid) — look at every protocol against the patterns |
| Deep-dive a specific protocol's fundamentals | `/web3-vc:unit-economics <slug>` | Part 2 (derived ratios) + Part 3 (quality screens) + sector-specific section in Part 4 |
| Find candidate protocols matching a thesis | `/web3-vc:scout <thesis-hint>` | Part 5 momentum rows + Part 3 concentration screens |
| Track LP / trader / MM behavior on a protocol (Phase 1) | `/web3-vc:onchain <slug>` | Sector-specific microstructure rows in Part 4 |
| Synthesize all of the above into a thesis (Phase 1) | `/web3-vc:thesis <vertical>` | The whole doc as scaffolding; the thesis must address the dominant Signal Grid rows |
| Watch governance + commits for narrative shifts (Phase 1) | `/web3-vc:watch <slug>` | (Out of scope for this doc — qualitative layer) |

---

## Appendix A: Reference ranges by sector (quick lookup)

| Sector | Healthy fees/TVL (annualized) | Healthy volume/TVL (monthly) | Typical take rate | Notes |
| --- | ---: | ---: | ---: | --- |
| Spot DEX (V2 AMM) | 10–30% | 1–5x | 0% (to LPs) | Race-to-bottom on fee tiers |
| Spot DEX (V3 CLMM) | 50–200% | 20–100x | 0% (to LPs) | But LP active management required |
| Spot DEX (stableswap, Curve) | 3–15% | 0.5–3x | 50% to veCRV | Low IL, low spread |
| Perp DEX (oracle, GMX) | 25–80% | 5–20x | 30% | LPs take counter-party risk |
| Perp DEX (orderbook, HL/dYdX) | 100–500%+ | 100–500x | 0–20% | Capital is collateral against leverage |
| Lending (Aave-style) | 2–6% | n/a | 10–20% reserve factor | Utilization 60–80% optimal |
| Yield aggregator | 2–8% | n/a | 10–20% perf fee | Quality depends on underlying |
| LST | 0.3–0.7% (of staked ETH) | n/a | 5–15% commission | Validator-set risk |
| Stablecoin issuer | Float income (e.g., 5% T-bill yield) | n/a | 100% to issuer | Highly profitable, regulated |
| Bridge | 5–20% | n/a | 50–100% | Concentration risk on bridged assets |

## Appendix B: Things this doc deliberately does NOT cover

- **Token unlock schedules** — read tokenomics docs / TokenUnlocks dashboard.
- **Smart-contract security** — read audit reports (Trail of Bits, OpenZeppelin, Spearbit).
- **Regulatory risk** — out of scope for quantitative metrics; needs legal monitoring.
- **Macro crypto market conditions** — BTC dominance, ETH/BTC, stablecoin supply growth — these are the *context*, not the *protocol-level* signal.
- **Token launch valuation framework (FDV-vs-circ play)** — separate methodology, often more important than P/S for sub-1yr-old tokens.
- **Specific investment recommendations** — never. This doc is methodology only.

---

## Appendix B+: Companion doc — Research Output Template

This metrics doc tells you **what to measure**. For **how to package the measurements into a publication-grade research piece**, see the companion doc:

→ [`research-output-template.md`](./research-output-template.md)

That doc reverse-engineers the writing template used by top crypto VCs (Paradigm / Multicoin / a16z Crypto / Variant / Delphi) from their public articles and benchmarks our own outputs against them.

Key takeaways:

- **Universal structure**: thesis statement → market opportunity (TAM) → case for X (team + mechanism + risk) → why long/short X → optionality scenarios
- **7 evidence types**: on-chain / TAM math / financials / competitive / mechanism / founder / stress test — top VC pieces use 5-7 of these
- **3-5 designed charts**, not markdown tables — visualization is part of credibility
- **Cross-validation finding (Aave VC Thesis 2026-05-25)**: our outputs are **stronger in rigor + reproducibility** but **weaker in storytelling + founder analysis + designed visuals** vs Multicoin Ethena benchmark

Read `research-output-template.md` before publishing any research artifact.

## Appendix C: When to re-read this doc

- **Quarterly.** Web3 metric norms drift. Healthy fees/TVL ranges shift with market cycles.
- **When a new sector emerges.** The first time you analyze a category not covered here (intents, account abstraction, AI agents on-chain), extend the framework explicitly — write a new Part 4 subsection.
- **When you make a wrong call.** If a thesis backed by these metrics turned out wrong, ask which part of the framework missed it. Update Part 6 (Common traps).
