# Crypto VC 研究输出模板

> **本文档目的**：从顶级 crypto VC（Paradigm / Multicoin / a16z Crypto / Variant / Delphi）公开发布的研究中**逆向工程**出他们的写作模板，让我们的研究产出能向行业最高标准看齐——同时保留我们独有的方法论优势。
>
> **基于实证 benchmark 数据 2026-05-25**，包含对 Aave VC Thesis v2 (2026-05-25) 的交叉验证审计。

---

## Part 1：跨 VC 共性结构（80%+ 通用模板）

### 1.1 通用结构骨架

所有顶级 VC 投资论文都遵循以下 5 段结构（无论赛道）：

```text
┌─ Opening ────────────────────────────────────────────┐
│ Thesis statement OR data hook (1-2 段)              │
│  • "Today we're announcing..."  (Multicoin 模式)    │
│  • "X charts on Y"              (a16z 模式)         │
│  • "Why X matters now"          (Paradigm 模式)     │
└──────────────────────────────────────────────────────┘
              ↓
┌─ Market Opportunity ─────────────────────────────────┐
│ TAM + tailwinds + market structure                   │
│  • "$X today → $Y by 20YY"  (必有 TAM 数学)        │
│  • 3 systemic forces / catalysts                    │
│  • Visual: 1-2 charts (TAM size, growth curve)      │
└──────────────────────────────────────────────────────┘
              ↓
┌─ The Case for X ─────────────────────────────────────┐
│ 单点 protocol / project 深度                         │
│  • Team / founder execution history                  │
│  • Mechanism description (how it actually works)     │
│  • Risk management + stress test history             │
│  • Value capture mechanics                           │
│  • Visual: 2-3 charts (protocol metrics, comp)       │
└──────────────────────────────────────────────────────┘
              ↓
┌─ Why We Are Long/Short X ────────────────────────────┐
│ Investment rationale + forward scenarios             │
│  • Explicit conviction language                      │
│  • Optionality narrative (additional upside)         │
│  • Time horizon                                      │
└──────────────────────────────────────────────────────┘
              ↓
┌─ (Optional) Risks / Limitations ────────────────────┐
│ 注意：top VC 通常把 risk EMBED 在 case 内（不拆出来）│
│ 拆出来反而 weaken thesis（顶级 VC 学到的反直觉技巧）│
└──────────────────────────────────────────────────────┘
```

### 1.2 必备的 7 类证据（任一研究都该有 4+ 类）

| 类型 | 例子 | 哪里拿 |
| --- | --- | --- |
| **On-chain data** | USDe 流通供应曲线 / Aave 30d fees | DefiLlama / Dune / 协议自身 dashboard |
| **TAM mathematics** | "$300B 当前 → $1T+ 五年内" | 行业研报 + 类比传统市场 |
| **Revenue / financials** | "$600m total revenue / $450m past 12mo" | Token Terminal / DefiLlama |
| **Competitive analysis** | "USDT/USDC 80%+ duopoly" | 市占率快照 + 时间序列 |
| **Mechanism description** | Delta-neutral basis trade 详解 | 协议白皮书 / 代码 / docs |
| **Founder / team quotes** | "I quit my job after Luna collapsed" | Twitter / 播客 / Interview |
| **Stress test case studies** | Bybit $1.4B hack, Oct 10 liquidation event | 历史事件 + 链上数据 |

**纪律**：每个**重大 claim** 必须有至少 1 类支撑证据。Multicoin Ethena 一篇用了**全部 7 类**。

### 1.3 通用 length + 配图规范

| 维度 | 顶级 VC 标准 | 备注 |
| --- | --- | --- |
| Word count | 3,000-6,000 字 / 10-20 min read | Paradigm 偏短（深度技术）, Multicoin 偏长（thesis-driven）|
| 图表数 | 3-5 charts | 每张图都是 reference point，不是 decoration |
| 章节深度 | H1 + H2 + H3 + H4（4 级嵌套）| 复杂主题用嵌套 scaffold |
| 行内引用 | 必须可点击溯源 | 链 onto 链上数据 / 协议 docs / 监管文档 |
| 结论语气 | 显式承诺 | "We invested in X" / "We are long Y" — 不藏 conviction |

---

## Part 2：各 VC 的 distinctive moves

### Paradigm

> **结构定位**：研究-工程实验室外壳的 VC 基金。研究文章常常**伴随他们 build 的 artifact**（Reth, Centaur, Blend）。

**特色 move**：
- **Open-source 机制创新**：写文章 = 发布开源工具。Blend (NFT lending) / Uniswap V3 concentrated liquidity / bullseye liquidity 都是先研究后释放
- **政策 brief 风格**：comment letter 形式参与 SEC / CFTC / OCC 规则制定，体现机构话语权
- **跨学科技术深度**：cryptography → game theory → protocol design 链式推理

**最近代表作**：
- "PACTs: Protecting Your Bitcoin From a Quantum Sunset" (2026-05-01) — 量子计算 vs BTC
- "Reth 2.0!" (2026-04-08) — 自己 build 的 Ethereum execution client
- "Intent-based architectures and their risks" — 微观结构深度

**何时模仿 Paradigm**：当你的研究**伴随你 build 的东西**（GitHub repo / 工具 / open source artifact）时——这正是 web3-vc plugin 的处境。

### Multicoin Capital

> **结构定位**：thesis-driven institutional conviction 风格。

**特色 move**：
- **Investment announcement + thesis 一体**：每篇文章 = 一次公开持仓+理由披露。"Today we're proud to announce we invested in X"
- **3 systemic tailwinds 模板**：开篇必列三大宏观驱动力（"Stablecoins / Perpification / Tokenization" 是 Ethena 用的）
- **多层产品 roadmap 作为 upside**：把"未来可能 ship 的产品"当 additional upside scenarios

**最近代表作**：
- "Ethena: Synthetic Dollars Challenge Stablecoins Duopoly" (2025-11-13) — **本文档主要 benchmark**，~4,800 字 16 min read
- "RWAs Are Just Built Different" (2026-03-19) — RWA 框架重写
- "Internet Labor Markets" (2026-03-10) — 新赛道开辟

**何时模仿 Multicoin**：当你在写**对单一 protocol 的 conviction（long 或 short）**时——VC thesis 标准结构最适合。

### a16z Crypto

> **结构定位**：data-heavy + mass accessibility。

**特色 move**：
- **"N charts" 系列**："7 Charts: Tokenized assets...", "9 charts on what stablecoins are becoming" — 数据可视化即整篇文章
- **Terminology 重新定义**：发文挑战行业默认术语（"Why 'stablecoins' won't age well"）— 通过定义权抢话语
- **Tag + 检索友好**：每篇文章打 4-6 个 tag（research / engineering / policy / GTM）

**最近代表作**：
- "7 Charts: Tokenized assets have proved the concept" — 数据 driven
- "3 product-market fit patterns that are working in crypto right now" — 模式归纳
- "Arcade tokens: The most underappreciated token type" — 定义新概念

**何时模仿 a16z**：当你想**用数据图表替代长 prose 论证**时——这种风格在 Twitter / LinkedIn 二次传播效果最好。

### Variant Fund

> **结构定位**：consumer / social-first crypto——和上面三家分赛道差异化。

**特色 move**（基于行业认知，未直接抓到文章）：
- 偏 consumer protocol 视角（不是 infra）
- 关注 ownership rails / social graphs
- 早期阶段为主

### Delphi Digital

> **结构定位**：subscription-gated 结构化深度报告（PDF 风格）。

**特色 move**（subscriber-only，没拿到具体样本）：
- 季度 sector report 形式
- 报告通常 30-50 页 PDF
- 多有清晰 executive summary + table of contents

---

## Part 3：与 Aave VC Thesis v2 (2026-05-25) 的交叉验证

### 3.1 我们做对的部分（与顶级 VC 一致或超越）

| 维度 | Aave thesis v2 | 顶级 VC 标准 | 评分 |
| --- | --- | --- | --- |
| Thesis statement opening | ✓ "PASS / UNDERWEIGHT" 在 Executive Summary 顶部 | ✓ 必有 | 🟢 |
| 多源数据证据 | ✓ DefiLlama + Dune + CoinGecko 三源 | ✓ 4+ 类 | 🟢 |
| 显式 investment recommendation | ✓ 单名 PASS + 赛道 OVERWEIGHT 拆分 | ✓ 必有 | 🟢 |
| 时间窗口明确 | ✓ "3-5 年（VC 基金生命周期）" | ✓ 必有 | 🟢 |
| Engineering audit appendix | ✓ Appendix Z 完整数据溯源 | ✗ VC 通常不做 | 🟢 **超越** |
| Falsifiable predictions | ✓ 5 个带概率的 prediction | ✗ VC 通常不做 | 🟢 **超越** |
| Multiple expression vehicles | ✓ 5 种打法（token/LP/vault/curator/pass）| ✗ VC 通常 just 一个 | 🟢 **超越** |
| Tool-stack disclosure | ✓ web3-vc plugin v0.2.0 标注 | ✗ VC 不做 | 🟢 **超越**（reproducibility signal）|

### 3.2 我们缺失的部分（vs 顶级 VC）

| 缺失项 | 顶级 VC 标准 | 影响 | 优先级 |
| --- | --- | --- | --- |
| **TAM 数学** | "$X 当前 → $Y 五年" | 缺这条让 thesis 缺乏"为什么现在"的紧迫感 | ⭐⭐⭐ 高 |
| **Team / founder execution 评估** | Multicoin Ethena 用了 Guy Young 起源故事 | Aave 的 Stani Kulechov / Morpho 的 Paul Frambot 等人决定 V4 / 范式扩张能否兑现 | ⭐⭐⭐ 高 |
| **详细 mechanism description** | Multicoin 详解 delta-neutral basis trade | Aave V4 的模块化 / GHO 的稳定机制 / Morpho 的 isolated market 风险隔离——这些机制细节是 conviction 的根本 | ⭐⭐ 中 |
| **Stress test case studies** | Multicoin 用 Bybit hack + Oct 10 liquidation 验证 Ethena 韧性 | Aave 在 2022 LUNA / 3AC / FTX 的具体响应 vs Morpho/Compound——这是评估护城河强度的最硬证据 | ⭐⭐⭐ 高 |
| **Designed charts** | Multicoin 4 charts, a16z 整篇文章是 charts | 我们 thesis 只有 markdown table，没有真正设计的视觉证据 | ⭐⭐ 中 |
| **Risk embedded in case (not separated)** | 顶级 VC 把 risk 写进 bullish case 内 validate thesis；我们拆成 bear case section | 拆开会 weaken 整体 conviction (虽然 academically 更严谨) | ⭐ 低（设计选择）|
| **Optionality narrative** | Multicoin 把"Ethena Whitelabel / HyENA" 当 multiplicative upside | 我们提了 Aave V4 / GHO / RWA 但没量化每个的 multiplier | ⭐⭐ 中 |
| **结论的承诺语气** | "We're excited as long term ENA tokenholders" | 我们偏学院派 ("Decision: PASS")——对 VC 受众而言可能太冷 | ⭐ 低（受众适配）|

### 3.3 我们独有的、顶级 VC 也少做的部分

| 独有 move | 价值 |
| --- | --- |
| **Engineering audit (Appendix Z)** | 数据溯源链清晰，所有数字 traceable 到原始 endpoint。这是学术研究标准，VC 圈很少做——但**正是 institutional LP 评估研究质量的关键** |
| **多重击点定价** | 给出 5 种"打法"而非 single bet。VC 圈通常 commits to single position。我们的多重击点对**多策略 fund / family office** 受众更友好 |
| **Methodology framework 显式声明** | Porter 5 forces → 3 questions → bridge audit。VC 圈很少 disclose framework，直接给结论。我们的显式 framework 让外部 reader 可以**独立 stress test** |
| **Tool-stack reproducibility** | web3-vc plugin GitHub 公开，任何人可以 fork + 跑同样数据。VC 圈研究通常黑盒。这是 **trust 和 portfolio 信号** |

### 3.4 综合评分：我们 vs Multicoin Ethena (本 benchmark 标杆)

| 维度 | Aave thesis v2 | Multicoin Ethena | 评估 |
| --- | --- | --- | --- |
| Word count | ~5,500 | ~4,800 | 接近 ✓ |
| 章节嵌套深度 | H1 + H2 + H3 | H1 + H2 + H3 + H4 | 我们少一级 |
| 证据类型 (7 类) | 4/7（缺 founder, mechanism, stress test）| 7/7 | **差距明显** |
| Charts | 0（只 tables）| 3-4 designed charts | **差距明显** |
| Reproducibility | ⭐⭐⭐ (full open source tool + data) | ⭐ (Token Terminal screenshots) | **我们胜** |
| Conviction tone | 中性偏冷 | 热烈承诺 | 视受众适配 |
| Optionality scenarios | 显式 base/bull/bear w/ probs | 隐式 optionality narrative | 各有优势 |
| Engineering audit | ⭐⭐⭐ Appendix Z | 无 | **我们胜** |

**净评估**：我们的 thesis 在 **rigor + reproducibility** 维度超越 Multicoin Ethena，但在 **storytelling + visualization + founder analysis** 维度落后。这是**研究型分析师**特征 vs **VC partner 投资思维**特征的差异。

---

## Part 4：未来研究产出的执行 checklist

每篇新研究产出**至少满足**以下：

```text
[ ] Opening: 1-2 段 thesis statement 或 data hook
[ ] 时间窗口明确（"3-5 年" 或 "12-18 个月"）
[ ] 5+ 类证据：on-chain + TAM math + financials + competitive + 
    mechanism + 至少一项 founder / stress test
[ ] 3-5 designed charts (不是 markdown table；用 Excalidraw / 
    matplotlib / Datawrapper 输出)
[ ] H1 + H2 + H3 + H4 至少 3 级嵌套
[ ] Explicit investment recommendation (BUY / SELL / PASS / OVERWEIGHT)
[ ] 至少 1 个 stress test case study（历史事件 + 实际响应）
[ ] 至少 1 段 team / founder execution 分析
[ ] Optionality narrative in conclusion（"如果 X 兑现，额外 upside 是 Y"）
[ ] Engineering audit appendix（数据溯源链）— 我们独有，必须保留
[ ] Falsifiable predictions w/ probabilities — 我们独有，必须保留
[ ] Word count 3,000-6,000 / 10-20 min read
[ ] All data points cite source endpoint (DefiLlama API, Dune query ID, etc.)
```

---

## Part 5：每个 Phase 的工具映射

```text
Opening (thesis statement)            → 你自己写
Market Opportunity (TAM, tailwinds)   → /web3-vc:sector + 手工 TAM 数学
The Case for X (单点深度)             → /web3-vc:fundamental + 手工 mechanism description
Stress test case studies              → 手工 + Dune historical liquidation queries
Team / founder analysis               → 手工 + WebSearch (interviews, Twitter)
Charts (3-5 designed)                 → matplotlib + Datawrapper（未来工具补充）
Optionality scenarios                 → 手工
Engineering audit (Z)                 → 我们 plugin 内置（独有 advantage）
Falsifiable predictions               → 手工（受我们 framework 约束）
```

**Phase 1 工具缺口（next plugin work）**：

1. **Designed chart generation** — 加个 `/web3-vc:chart` skill，用 matplotlib 把 DefiLlama / Dune 数据画成 publication-quality png
2. **Stress test case study database** — 加个 `data/stress-tests.md`，记录 LUNA / 3AC / FTX / Oct 10 等历史事件对每个 protocol 的响应
3. **Team / founder profile fetcher** — 集成 Twitter / podcast search 抓 founder quotes（用 `x-mcp`）

这些是 **真正让我们的研究产出从"分析师 quality" 升到 "VC partner quality"** 的下一步。

---

## Sources

- [Paradigm Writing](https://www.paradigm.xyz/writing)
- [a16z Crypto Posts](https://a16zcrypto.com/posts/)
- [Multicoin Capital Blog](https://multicoin.capital/)
- [Multicoin Ethena Investment Thesis (benchmark)](https://multicoin.capital/2025/11/13/ethena-synthetic-dollars-challenge-stablecoins-duopoly/)
- [Paradigm Intent-Based Architectures](https://www.paradigm.xyz/2024/04/intent-based-architectures-and-their-risks)
- F4.fund 分析: [Paradigm — Investment Thesis & Preferences](https://f4.fund/firms/paradigm)
- [Crypto VC Performance Rankings (KaitoAI via Crypto.news)](https://crypto.news/paradigm-leads-kaitoais-crypto-vc-performance-rankings/)
