---
description: Web3 协议基本面深度审计 — token 分类 → 数据拉取 → 五层指标 → 价值捕获桥审计 → 戈登模型反推 → 结构化报告
argument-hint: "<protocol-slug>  (DefiLlama slug, e.g. aave / pendle / hyperliquid)"
---

Load the `fundamental` skill and run a full single-protocol fundamental audit for **`$ARGUMENTS`**.

This skill uses the DefiLlama MCP tools (`protocol_detail`, `protocol_fees`) plus a CoinGecko fetch for FDV cross-check, then walks the "value capture bridge" methodology end-to-end and writes a structured report to `./fundamentals/{slug}-{date}.md`.

If `$ARGUMENTS` is empty, ask the user for the target slug before doing anything.
