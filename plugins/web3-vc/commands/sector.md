---
description: Web3 赛道结构研究 — 波特五力 → 三问框架，DefiLlama (breadth) + Dune (depth) 双层数据。输出选股表 + 择赛道分 + 喂回 /fundamental 的 g/m 锚
argument-hint: "<sector>  (lending / dexs / derivatives / yield / rwa / stablecoins / liquid-staking)"
---

Load the `sector-scan` skill and run a 4-phase sector structural research for **`$ARGUMENTS`**.

- **Phase A** pulls breadth data via DefiLlama (TVL, fees, take-rate distribution, HHI snapshot)
- **Phase B** optionally pulls depth data via Dune MCP (share migration, deposit concentration, liquidations, unified-metric HHI) — requires `DUNE_API_KEY` configured; if absent, skips gracefully with explicit note in the report
- **Phase C** synthesizes Porter's 5 forces with quantitative evidence (one line of data) per force
- **Phase D** writes `./sectors/<sector>-<date>.md` with a **dual view**: (1) capture-adjusted protocol ranking (selection orientation) and (2) sector attractiveness score 0–100 (allocation orientation), plus explicit anchors for `/web3-vc:fundamental` (g anchor + m anchor)

If `$ARGUMENTS` is empty, ask the user: (a) which sector, and (b) whether the goal is **selection** (best protocol within sector) / **allocation** (whether the sector itself is worth a basket position) / **both** — before starting Phase A.
