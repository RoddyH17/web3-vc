---
name: fundamental
description: Web3 协议基本面深度审计 — 通过 DefiLlama MCP 工具拉数据，对单一协议做"价值捕获桥"五层审计，戈登模型反推市场隐含增长率，输出结构化报告。比 unit-economics 更严谨（多了 holder capture 命门 + 反推 + 敏感性矩阵），适合做 conviction call 前的最后一步深度尽调。Use when asked to "do a fundamental audit", "deep dive a protocol", "audit value capture", "reverse-engineer implied growth", or "bridge audit". Triggers on "fundamental", "value capture bridge", "holder capture", "implied growth", "Gordon model", "buyback yield".
---

# Web3 Protocol Fundamental Audit

## 核心信念（务必内化，它决定了整个分析视角）

> Web3 基本面研究的中心，**不是**「协议有没有收入」，而是
> **「token 为什么能拿到这部分收入」**。
> 「协议创造了价值」和「token 持有者拿到了价值」之间隔着一座**桥**。
> 估值研究的全部重点，就是审计这座桥有多宽、正在变宽还是变窄。
>
> **DCF 不是第一步，倍数 (P/S, P/F) 也不是第一步。**
> 它们都是审计完桥之后、最后一步才用的工具。

**绝不跳过审计直接报一个 P/S 数字**——那正是这套方法论要反对的「粗暴 P/S」。

---

## 执行流程

```text
Step 0  解析参数 & 判定 token 类型
Step 1  通过 MCP 拉取 DefiLlama 数据 + CoinGecko 补 FDV
Step 2  计算五层指标 + 自洽校验
Step 3  审计「价值捕获桥」（五层逐层判断 + 灯号）
Step 4  反推市场隐含假设（戈登 + 3×3 敏感性 + 回购收益率）
Step 5  输出结构化报告（写入 ./fundamentals/<slug>-<date>.md）
```

---

## Step 0 — 解析参数 & 判定 token 类型

`$ARGUMENTS` 是 DefiLlama 上的协议 slug。先做两件事：

### 0.1 确认 slug
slug 通常是小写、连字符分隔（`aave`、`uniswap`、`gmx`、`hyperliquid`、`ethereum`）。若用户给的是 ticker 或大小写不规范，先归一化。若不确定，调 `list_protocols()` 拉清单搜名字。

### 0.2 分类 token，再选方法

| Token 类型 | 合适框架 | 关键指标 | 忌讳 |
|---|---|---|---|
| L1 原生资产 (ETH/SOL) | 货币溢价 + 网络价值 + 验证者视角 DCF | fees、burn、staking yield、活跃地址 | 单纯 P/S |
| L2 token | Sequencer 价值 + 治理 | fees、MEV、DA、treasury | 只看 TVL |
| DEX / Perps | Revenue multiple + take rate | volume、fees、holder revenue | 只看 volume |
| Lending | Revenue + 风险调整 TVL | borrows、utilization、bad debt | 只看 deposits |
| LST / Restaking | AUM take rate | staked assets、net spread | 只看 TVL |
| Yield / 衍生品 | 自成一类，看市占率 + 增长 | underlying TVL、holder revenue | 硬套 DEX 基准 |
| DePIN | 单位经济学 + work token/BME | supply capacity、paid demand | 只看节点数 |
| Stablecoin 发行方 | Reserve yield + 监管 | supply、净息差 | 普通 P/S |
| Meme / 文化 | 反身性 + 流动性 | holders、volume、mindshare | DCF / P/S |

**关键纪律：同赛道才能比。** 不同赛道的「健康」基准差几十倍，跨赛道比比率毫无意义。

在报告里**明确写出分类结论**，因为它决定后续每一层的解读基准。

---

## Step 1 — 通过 MCP 拉数据

### 1a. 一次拉完协议侧基础数据

调用 **`protocol_detail(slug)`** 一次拿到：

- Supply (deposits) TVL — 已经正确剔除 `-borrowed` / `-staking` / `-pool2` 重复计数
- Borrowed（仅 Lending 类）
- Utilization（仅 Lending 类，自动算好）
- 各链 TVL 分布表
- Market Cap (DefiLlama，可能为 null)
- FDV (DefiLlama，**经常为 null**)
- gecko_id（供 CoinGecko 补 FDV 用）
- Category / chains / token symbol

### 1b. 一次拉完三个 dollar stream

调用 **`protocol_fees(slug)`** 一次拿到（内部会自动打三个 dataType endpoint 并合并）：

- Fees（用户付的总费用）24h/7d/30d/all-time
- Revenue（协议留的部分）24h/7d/30d/all-time
- **Holders Revenue**（真正到 token 持有者的部分）24h/7d/30d/all-time —— **这是桥的命门**
- Annualized run-rate（30d × 12）
- **Take rate** = Revenue / Fees
- **Holder capture rate** = Holders Revenue / Revenue（含 "bridge near-broken" ⚠️ 警告灯）
- Lifetime 对比（current vs lifetime holder capture，含 ↑/↓/≈ 趋势）

若工具返回 "Not indexed"，**把缺失本身当作发现**——在报告里高亮，不要静默跳过。

### 1c. CoinGecko 补 FDV（必要时）

如果 `protocol_detail` 的 FDV 字段为 null（很常见），用 `Bash` + curl 补：

```bash
curl -s "https://api.coingecko.com/api/v3/coins/{gecko_id}?localization=false&tickers=false&community_data=false&developer_data=false&sparkline=false"
```

取 `market_data.fully_diluted_valuation.usd`、`market_data.market_cap.usd`、`market_data.circulating_supply` / `total_supply` / `max_supply`。

若用户在对话中已手动给过 FDV，**优先用用户的数字**并注明来源。

### 1d. 赛道数据（供 Step 4 r/g 校准）

可选：调 `list_protocols(category="<Sector>", top_n=10)` 看该协议在赛道里的相对位置（market share）。这一步主要是为 Step 4 反推 g 时校准"行业整体增速 vs 该协议增速"的参考。

### 数据卫生

- 每个原始数字记下**来源工具 + 调用时间**。报告里所有计算可追溯到原始字段。
- 遇到荒谬数字（如 take rate > 100%）**先怀疑口径**，回查原始返回。
- 遇到多来源打架（DefiLlama mcap vs CoinGecko mcap，TVL 不同口径），**两个口径都报**，并说明差异会让结论差几倍。

---

## Step 2 — 计算五层指标

用 Step 1 的数据计算下列比率（许多已由 `protocol_fees` 自动算好，只需读取）。

### 2.1 资本效率（除以 Supply TVL，不是 borrowed-inflated 数字）

- **Fees / TVL（年化）** = 年化 Fees / Supply TVL → 每块锁仓资本的总产出
- **Revenue / TVL（年化）** = 年化 Revenue / Supply TVL → 货币化率
- （DEX/Perp 适用）**Volume / TVL（月）** → 资本周转速度

### 2.2 抽成与捕获

- **Take rate** = Revenue / Fees → 协议从总费用里抽走的比例
- **Holder capture rate** = Holders Revenue / Revenue → **桥的宽度**
- **补贴占比** = Incentives / Fees → fee 里多少是发币补贴催出来的（手工估算，未在 MCP 中）

### 2.3 净值与稀释

- **Earnings ≈ Revenue − Incentives** → 真净利
- **MC / FDV** → 越接近 1 越无未来稀释

### 2.4 估值倍数（最后一步）

- **P/F** = FDV / 年化 Fees
- **P/S** = FDV / 年化 Revenue
- **P / Holders Revenue** = FDV / 年化 Holders Revenue（**桥断裂时这才是真倍数**）
- **自洽校验**：`P/S ÷ P/F` 应当 ≈ `1 / take rate`。算出来对不上就是数据/口径问题，回查。

### 2.5 赛道健康基准对照

| 赛道 | Fees/TVL 健康 | 平庸 | 危险 |
|---|---|---|---|
| Spot DEX (AMM) | >15% | 5–15% | <5% |
| Perp DEX (oracle, GMX) | >25% | 10–25% | <10% |
| Perp DEX (orderbook, dYdX/HL) | >100% | 50–100% | <50% |
| Lending | >5% | 2–5% | <2% |
| LST (commission base) | >0.5% | 0.2–0.5% | <0.2% |
| Yield aggregator | >5% (of underlying) | 2–5% | <2% |

| Revenue/TVL | 含义 |
|---|---|
| <0.5% | 货币化极差，token 几乎一无所获 |
| 0.5–3% | DeFi 蓝筹平均 |
| >3% | 强货币化 |

| Take rate | 商业模式画像 |
|---|---|
| 0% | 纯 LP 供养 (Uniswap V3 默认) |
| 5–15% | 温和 (Maker 稳定费 / Aave 储备金) |
| 20–40% | 激进 (GMX, dYdX 历史) |
| >50% | 实质收租，仅强护城河可持续 |

| P/S | 隐含定价 |
|---|---|
| <5x | 深度价值（或垂死，查增长）|
| 5–15x | 成熟蓝筹 |
| 15–40x | 成长定价 |
| 40–100x | 高成长 / 投机 |
| >100x | meme / 无收入 / 空气 |

---

## Step 3 — 审计「价值捕获桥」（五层逐层判断）

**逐层走，每层给出明确判断（🟢 / 🟡 / 🔴）**，不要只罗列数字。最终把每一项代入：

```text
Token 可捕获价值 = Fees × take rate × holder share − incentives − unlock dilution
```

### 第 1 层 · 产品层 — 用户愿意付费吗？(PMF)

- 看**补贴占比**。接近 0 → fee 真实需求（🟢）；很高 → 补贴催出的虚假繁荣（🔴）。
- （Lending 专属）看 **Utilization**（已由 `protocol_detail` 算好）。60–80% = 健康；<40% = 资本闲置；>90% = 流动性压力。
- 结论：判断 PMF 是否成立。

### 第 2 层 · 商业层 — 协议抽得到成吗？(Monetization)

- 看 **take rate** 落在哪档。
- 温和 take rate 不必然是缺点（亲 LP = 竞争力），但要评估赛道内可持续性。
- **Take rate trap**：高 take rate 会被低 take rate 竞品颠覆，护城河够深吗？

### 第 3 层 · 捕获层 — token 分得到吗？（桥的命门）⭐

- 看 **holder capture rate**。若 < 1% → 桥几乎断裂。`protocol_fees` 工具会自动加 ⚠️ 警告。
- **必须高亮**，并追问 revenue 去了哪：Treasury？LP/validator？被 emissions 抵消？
- 对比 **lifetime holder capture**（工具自动算）：
  - 若 lifetime >> current → 桥曾经更宽，最近 narrowing（可能 fee switch 关了 / buyback 暂停）
  - 若 lifetime ≈ current → 协议的"基线状态"就是这样
- 检查是否有 **fee switch / buyback / burn / staking 分红** 机制，以及是「已稳态运行」还是「仅治理提案」。
- 这一层几乎总是单项目估值的最大不确定性，**明确给出 🟢/🟡/🔴**。

### 第 4 层 · 稀释层 — 收益被发币抵消了吗？(Net Value)

- **MC / FDV**：接近 1 → 稀释快走完（🟢）；很小 → 未来抛压大（🔴）。
- **Earnings ≈ Revenue?** 是 → 不靠烧钱续命；负 → 在烧钱买增长。
- 若拿到 unlock schedule（手工查 TokenUnlocks），评估未来 12–24 个月稀释节奏。

### 第 5 层 · 定价层 — 市场给几倍？(Relative Value)

- **现在**才报 P/F 和 P/S，并且**必须结合前四层来解读**：
  - 低 P/F 别急着说「便宜」——若 take rate 低，便宜的是"整个生意"不是"你的 token"
  - P/S 的合理性取决于第 3 层：若 holder capture ≈ 0，则名义 P/S 严重低估真实估值，**必须同时报 `FDV / Holders Revenue` 作为对照**

---

## Step 4 — 反推市场隐含假设（核心增量步骤）

**这是这套方法论最有价值的部分。** 不要止步于「P/S 是 15x」，要反过来**拷问市场假设**。

### 4.1 理论根基

P/S 是戈登增长模型的压缩形式：

```text
P/S = m / (r − g)
```

- `m` = 可分配比例（revenue 转化为持有者价值的稳态比例）
- `r` = 折现率（投资者要求回报率，风险定价）
- `g` = revenue 永续增长率

反解隐含增长率：

```text
g = r − m / (P/S)
```

### 4.2 参数怎么设

**m（可分配比例）**：不要天真设 100%。用协议**实际的捕获承诺**锚定。

- 有明确 buyback 计划：`m ≈ 年回购额 / 年 Revenue`
- Fee switch 已开 + 有分红：用实际 holder capture rate
- 几乎不捕获（holder capture ≈ 0）：分别测试 m = 0.3 / 0.5 / 1.0 看敏感性

**r（折现率）**：crypto 远高于股票。经验区间：

- 龙头蓝筹：20–25%
- 成长型：25–35%
- 高风险 / 早期：35%+
- 默认取 22%（蓝筹）做中性估计

**约束**：戈登模型要求 `g < r`，否则公式失效。**若反推 g ≥ r，说明当前倍数已脱离基本面**（对应 P/S >100x 的「空气」档）——这本身是结论。

### 4.3 必须做 3×3 敏感性分析

让 r 和 m 各取低/中/高，输出隐含 g 矩阵。

**关键洞察**：m 越低（越怀疑 token 能捕获），撑起同一倍数所需的 g 越高——即「市场要么相信桥会修宽（高 m），要么相信增长很猛（高 g），至少信一个」。

示例格式：

```text
| | m=0.3 | m=0.5 | m=1.0 |
|---|---:|---:|---:|
| r=20% | g=?% | g=?% | g=?% |
| r=25% | g=?% | g=?% | g=?% |
| r=30% | g=?% | g=?% | g=?% |
```

### 4.4 回购收益率（Buyback Yield）— 桥「已建成段」的真实回报

若协议有 buyback：

```text
回购收益率 = 年回购额 / FDV（或 Market Cap）
```

对照传统坐标系（无风险国债 ~4–5%、标普股东总回报 ~3–4%），判断「当前确定回报」是否跑赢无风险利率。

**核心叙事**：买该 token = 当前回购收益率（桥已建成段）+ 对「回购额随 revenue 增长而扩大」的期权（桥继续施工的预期）。

### 4.5 反推的最终用途

给出一句话判断：

> **「在 [r=__, m=__] 假设下，当前 [P/S=__x] 隐含市场预期 revenue 永续增长 [g=__%]。这个增长率现实吗？」**

然后基于赛道与协议基本面给出**你的判断**（偏贵 / 合理 / 偏便宜），并说清这个判断**依赖哪个假设最敏感**。

---

## Step 5 — 输出结构化报告

把报告写入 `./fundamentals/<slug>-<YYYY-MM-DD>.md`。若目录不存在，先创建。

### 报告骨架（必须遵守）

```markdown
# 基本面审计：<协议名> ($TICKER)

## 0. 分类与数据快照
- Token 类型：__（及对应框架）
- 数据来源与时点：DefiLlama MCP + CoinGecko，<日期>
- 关键原始数据表（Supply TVL / Borrowed / Utilization / Fees / Revenue /
  Holders Revenue / FDV / Mcap）
- 口径警告：__（若有多口径差异，明确说明）

## 1. 五层指标
（一张表：所有比率 + 落在赛道基准的哪一档 + 自洽校验
 P/S÷P/F ≈ 1/take rate）

## 2. 价值捕获桥审计
### 第 1 层 · 产品层 [🟢/🟡/🔴]
### 第 2 层 · 商业层 [🟢/🟡/🔴]
### 第 3 层 · 捕获层 [🟢/🟡/🔴]  ← 重点
### 第 4 层 · 稀释层 [🟢/🟡/🔴]
### 第 5 层 · 定价层（解读，不打灯）

## 3. 市场隐含假设反推
- 3×3 敏感性矩阵（g 矩阵）
- 回购收益率（若适用）
- 一句话命题：付 __x 倍，买的是「__% 当前回报 + __ 增长期权」

## 4. 结论
- 桥公式逐项成色（哪几项绿灯、哪项是命门）
- 偏贵 / 合理 / 偏便宜，及最敏感的假设
- 可证伪的关键问题（看多/看空各取决于什么）
- 可立即纳入 watchlist 的指标（3 条以内）

> 本报告为基本面研究框架演示，非投资建议。链上数据口径多变，
> 所有结论依赖于所列假设（折现率 r、可分配比例 m 等），请独立验证。
> 数据时点：<timestamp>。30 天后比率会因市场波动重新校准，结论需重估。
```

---

## 重要原则（贯穿全程）

1. **先分类，再分析**；同赛道才能比
2. **遇到荒谬比率，先查口径**（如 take rate >100% 几乎一定是 fees/revenue 口径不一致）
3. **第 3 层（捕获）是命门**——单项目估值的不确定性几乎总集中在这里
4. **倍数永远是最后一步**，且必须结合前四层解读；低 P/F ≠ 便宜
5. **反推假设 > 接受结论**：不要只报 P/S，要算出市场隐含的 g 并拷问
6. **emissions 是成本**：高 APR 若来自增发，是稀释伪装成的收益
7. **数字可追溯**：每个计算都能回到原始 MCP 工具调用 + 字段名
8. 若数据缺失（如 Holders Revenue 为 null），**把缺失本身当作发现**

## Failure modes

- Protocol 不在 DefiLlama：停，告诉用户，建议手工 Token Terminal / Artemis 查
- Fees 未被 DefiLlama fees adapter 索引：仍可产 Step 2.1 + 2.3 部分，明确标注 P/S 无法计算
- 多链协议指标在不同链之间冲突：按 Supply TVL 主导链做主分析，其他链作为附录
- Lifetime holders revenue 远大于 30d holders revenue：高亮"桥曾经更宽"——可能 fee switch / buyback 被关闭，是重大基本面变化信号
