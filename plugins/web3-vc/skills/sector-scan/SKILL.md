---
name: sector-scan
description: Web3 赛道结构性研究 — 从波特五力借框架，收敛成"TAM 增长 / 集中度 / 利润率可持续性"三问，用 DefiLlama (breadth) + Dune (depth) 两层数据回答。输出两类信号：选股导向（赛道内 capture-adjusted 排序）与择赛道导向（整体结构吸引力打分）。为 /web3-vc:fundamental 的单点估值提供 g (隐含增长) 和 m (可分配比例) 的现实锚。Use when asked to "scan a sector", "do sector research", "sector structure analysis", "Porter five forces", "rivalry analysis", "share migration", or "is this sector worth allocating to". Triggers on "sector", "rivalry", "share migration", "concentration", "HHI", "take rate sustainability", "TAM growth".
---

# Web3 Sector Structural Research

## 核心信念

> 单点公司分析问"这家公司好不好"；
> 赛道分析问一个更上游的问题——
> **"这个行业的结构，决定了身处其中的公司能不能持续赚钱。"**
>
> 一个糟糕赛道里的优秀协议，往往跑不赢一个优秀赛道里的平庸协议。
> 赛道研究的最终用途，是给单点估值提供两个独立的现实锚：
>   - 给 `m` 锚（赛道 take rate 趋势 → 限制单点 holder capture 的上限）
>   - 给 `g` 锚（赛道 TAM 增速 → 限制单点合理隐含 g）
>
> 没有赛道锚，单点 `/fundamental` 的隐含 g 永远是悬空的。

---

## 框架：波特五力 → 三问

完整波特五力（Rivalry / New Entrants / Substitutes / Buyer Power / Supplier Power）必须在每个赛道场景里翻译成 web3 对应物（见 Step 3）。但作为可量化的分析骨架，五力收敛成 **三个赛道核心问题**：

```text
问题一: TAM — 赛道在变大还是变小?
   (前提：再好的结构，池子在缩也没用)
   主指标: 赛道总 TVL / fees / revenue 趋势, CAGR
   覆盖力: 五力的"前提"层
   数据源: DefiLlama (breadth)

问题二: 集中度 — 赢家通吃 vs 多强混战?
   (决定龙头能否维持定价权)
   主指标: HHI 集中度, 份额迁移一阶导, fork 蚕食率
   覆盖力: 五力第 1 (Rivalry) + 第 2 (New Entrants)
   数据源: DefiLlama (snapshot) + Dune (动态迁移)

问题三: 利润率 — take rate 会被打到趋零吗?
   (决定 take rate 能否维持，直接喂回 /fundamental 的 m)
   主指标: take rate 横向离散 + 时间趋势, 替代品收益率利差
   覆盖力: 五力第 3 (Substitutes) + 第 4 (Buyer) + 第 5 (Supplier)
   数据源: DefiLlama (take rate) + Dune (capital stickiness, 寄生结构)
```

**关键陷阱（必须在每次扫描时提醒自己）**：DeFi 赛道边界是流动的。Morpho 是"lending app"还是"lending infrastructure"？Pendle 算"收益率"还是"borrowing 的替代品"？Hyperliquid 的借贷模块算 perp 还是 lending？赛道分析必须**先明确边界**，否则数字会跨边界乱串。在报告里明确写出"本次扫描的赛道边界为 X，刻意排除 Y 因为..."。

---

## Inputs

`$ARGUMENTS` 是赛道名称：

- `lending` — money market 协议（Aave / Compound / Morpho / Spark / Fluid 等）
- `dexs` — spot DEX（Uniswap / Curve / Aerodrome / PancakeSwap 等）
- `derivatives` — perp / options DEX
- `rwa` — RWA tokenization
- `yield` — yield aggregators
- `stablecoins` — stablecoin issuers
- `liquid-staking` / `liquid-restaking`
- A chain name → 改为做 chain-level scan，不走这套五力框架（chain 不是商业实体，框架不适用）

如果用户没指定，先问"做哪个赛道"，并问"研究目的是 (a) 在赛道内选最强的协议（**选股导向**），还是 (b) 判断这个赛道整体值不值得配置（**择赛道导向**），还是 (c) 两者都要"。这决定了输出表的重点。

---

## 工作流（4 阶段）

```text
Phase A  DefiLlama breadth scan — 拉赛道全景
Phase B  Dune depth probes — 钻链上细粒度（动态迁移、集中度、坏账）
Phase C  五力综合 — 每一力给一个量化结论 + 灯号
Phase D  输出 — 双视角（选股表 + 择赛道分）+ 喂回 /fundamental 的锚
```

---

### Phase A — DefiLlama Breadth Scan

回答 **问题一（TAM）** 和 **问题二的 snapshot 部分**。

#### A.1 拉赛道全景

```text
list_protocols(category="<Sector>", top_n=20)
fees_overview(top_n=50)   # 后续过滤出该赛道协议
```

DefiLlama category 命名（必须精确）：
- `Lending` / `Dexs` / `Derivatives` / `Yield` / `RWA` / `Liquid Staking` / `Liquid Restaking` / `CDP` / `Bridge`

#### A.2 计算赛道层指标

| 指标 | 公式 | 用途 |
|---|---|---|
| 赛道总 TVL | Σ(top 20 协议 TVL) | 问题一基线 |
| 赛道 7d / 30d Δ | (now − prior) / prior | TAM 增速 |
| 赛道总 fees 30d (年化) | Σ(协议 fees_30d) × 12 | 真实赛道经济活动 |
| HHI (TVL 基准) | Σ(share^2) × 10000 | 问题二集中度 |
| 头部 take rate 离散 | std(top 5 协议 take rate) | 问题三定价权 |

HHI 解读：
- <1500: 竞争激烈（多强混战）
- 1500-2500: 中度集中
- 2500-7500: 高度集中（寡头）
- \>7500: 接近垄断

#### A.3 拉单协议补充数据（前 5 名）

对每个 top-5 协议调 `protocol_detail(slug)` + `protocol_fees(slug)` 拿到 fees/TVL、take rate、holder capture rate。**这一步用我们刚修好的 bug，确保拿到 supply TVL 而非 supply+borrowed 总和**。

---

### Phase B — Dune Depth Probes

回答 **问题二的动态部分** 和 **问题三的 capital quality 维度**。

> ⚠️ **Phase B 是 Phase 1 stub，依赖 Dune MCP 已配置**。
> 若用户未配 `DUNE_API_KEY`，跳过 Phase B 并在报告里明确标注"未配置 Dune，所有 depth 维度跳过；HHI 用 DefiLlama snapshot 替代"。
> 配置说明见 `connectors/dune/README.md`。

#### B.1 工作流（每个 Dune 调用都用 `executeQueryById` 或 `createDuneQuery` 接 SQL）

对 lending 赛道，使用 `connectors/dune/queries/lending/` 下的 5 个模板：

| SQL 模板 | 回答的问题 | 喂给五力 |
|---|---|---|
| `01-share-migration.sql` | "Morpho 多快地从 Aave 抽走资本？" | Force 1 (Rivalry) 动态证据 |
| `02-deposit-concentration.sql` | "top 10 LP 占多少 TVL？账户多老？" | Force 4 (Buyer Power) |
| `03-utilization-trend.sql` | "每天 borrows/supply 多少？谁在抢借款需求？" | Force 1 + 整体 PMF |
| `04-liquidation-volume.sql` | "清算事件 + bad debt 趋势" | Force 5 (Supplier — oracle/infra reliability) |
| `05-unified-hhi.sql` | "用 active borrows 而非 TVL 算 HHI，去除口径偏差" | Force 2 (Entrants) — 真实活动维度 |

**关键纪律**：每个 Dune SQL 模板都有 `⚠️ Schema-drift warning`——Spellbook 表名会变。**运行前先用 `searchTables` 验证表名**，再 `createDuneQuery` 提交。

#### B.2 SQL 模板使用流程

1. 用户调 `/web3-vc:sector lending`
2. 读 `connectors/dune/queries/lending/*.sql` 内容（用 Read 工具）
3. 对每个模板：
   a. 调 Dune MCP `searchTables` 找当前 Spellbook 里 Aave / Compound / Morpho 的真实表名
   b. 替换模板里的 `{{xxx_table}}` 占位符
   c. `createDuneQuery` 提交（注意 timeout 设为 300s）
   d. `executeQueryById` 跑
   e. `getExecutionResults` 取结果
4. 汇总到 Phase C

#### B.3 Credit 预算

每次完整 lending 赛道扫描 = 5 个 SQL × 1-2 次 execute = ~10 credits。Plus 套餐 ~1000/月，足够 30 次扫描/月。

---

### Phase C — 五力综合（带量化证据）

每一力给出 **灯号（🟢/🟡/🔴） + 一行量化证据**。不允许只给定性结论。

#### Force 1 · Rivalry (现有竞争激烈度)
- **量化证据**：Phase B 的 `01-share-migration` 30d 累计迁移额 / 龙头 TVL
  - <1% → 🟢 安全
  - 1-5% → 🟡 缓慢蚕食中
  - \>5% → 🔴 显著流失
- **配合**：Phase A 的 take rate 横向离散——离散小说明大家被迫贴近，rivalry 强

#### Force 2 · Threat of New Entrants (新进入威胁)
- **量化证据**：fork 数 + 前 5 名以外协议份额之和
  - 前 5 名占 >85% → 🟢 进入门槛实质有效（即使代码开源）
  - 前 5 名占 70-85% → 🟡 长尾在咬
  - 前 5 名占 <70% → 🔴 进入门槛很低，份额碎片化
- **特别注意**：Phase B 的 `02-deposit-concentration` 若显示头部 LP 老（>1 年）→ 品牌信任型护城河有效；若头部 LP 新（<3 月）→ 是 mercenary capital，进入门槛低

#### Force 3 · Threat of Substitutes (替代品威胁)
- **量化证据**：跨赛道收益率利差（DeFi supply APY vs T-bill vs Pendle 固定利率 vs CEX 理财）
  - 利差 <100bps → 🔴 替代品强，资金随时流出
  - 利差 100-300bps → 🟡 中性
  - 利差 >300bps → 🟢 该赛道收益吸引力强
- **数据来源**：DefiLlama yield aggregator 数据 + 手工补 T-bill (4-5%) 和 CEX 理财参考

#### Force 4 · Buyer Power (买方议价能力)
- **量化证据**：Phase B 的 `02-deposit-concentration` cumulative_pct + Phase B 的 `01-share-migration` 中的 distinct addresses
  - Top 10 LP >80% TVL → 🔴 几个大户的议价权极高，可以随时威胁迁移
  - Top 10 LP 50-80% → 🟡 典型 DeFi 集中度
  - Top 10 LP <50% → 🟢 分布式存款基础，没有单一议价力
- **DeFi 特殊性**：切换成本 ≈ 0，所以即使分布式，整体买方议价仍强（这是赛道层的结构性问题，所有协议共担）

#### Force 5 · Supplier Power (供方议价能力)
- **DeFi 的"供应商"**：
  - 流动性提供者 (LPs / depositors) → 已在 Force 4 量化
  - 底层基础设施 (Chainlink oracle, ETH gas, L2 sequencer)
  - 寄生结构（Morpho 把 Aave 当流动性来源 → 反向 supplier power 削弱了 Aave）
- **量化证据**：Oracle 集中度（Chainlink 在该赛道的占比）+ 是否有寄生协议（Morpho-style）抽走 spread
  - 单一 oracle + 有寄生协议 → 🔴
  - 多 oracle + 无寄生 → 🟢

---

### Phase D — 输出

写入 `./sectors/<sector>-<YYYY-MM-DD>.md`。

#### D.1 必须的两类输出（兼顾选股 + 择赛道）

**(1) 选股表 — capture-adjusted 排序**

```markdown
| Rank | Protocol | Annual Fees | Annual Revenue | Annual Holders Rev | P/F | P/S | P/HR | Force 1 share-loss | 综合灯号 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
```

按 **"holder capture 调整后的 P/Holders Revenue"** 排序，不按 P/S 排序——这是这套方法论的核心：不要被"漂亮但抓不住价值"的 token 骗到。

**(2) 择赛道分 — 单一数字（0-100）**

赛道结构吸引力 = 加权 (TAM 增速 × 25%) + (1 - HHI 极端度 × 25%) + (take rate 稳定性 × 25%) + (5 力综合灯号 × 25%)

每项 0-100，加权得分用来跨赛道对比。例如：
- Lending: 62/100（TAM 稳定，HHI 中度集中，take rate 被 Morpho 压低）
- Perp DEX: 78/100（TAM 暴涨，HHI 高度集中 Hyperliquid 主导，take rate 有 token economics 保护）
- 据此判断"在 lending 多配 vs 在 perp 多配"

#### D.2 必须的"喂回 /fundamental"块

```markdown
## Anchors for /fundamental

赛道 g 锚: trailing-12m revenue CAGR = __%
  → 任何单点协议隐含 g 显著高于此值，需要论证"凭什么抢份额"
  → 任何单点协议隐含 g 显著低于此值，可能被低估

赛道 m 上限: take rate 头部 median = __% × 经验 holder pass-through 0.3 = __%
  → 单点协议假设 m > 此值，需要论证"有什么独特的捕获机制"
```

#### D.3 报告骨架

```markdown
# 赛道结构研究：<赛道名> — <date>

## 0. 赛道边界声明
- 本次扫描包含：<具体协议列表>
- 刻意排除：<协议> 因为 <理由>（例：寄生协议、跨赛道、纯衍生品等）
- 研究目的：选股 / 择赛道 / 双视角

## 1. 赛道三问回答（Phase A + B 综合）
- 问题一 TAM：<增长率> ± <置信度评论>
- 问题二 集中度：HHI = <值>，<解读>，份额迁移趋势 <描述>
- 问题三 利润率可持续：take rate trend <描述>，替代品利差 <值>

## 2. 波特五力评分（Phase C）
- Force 1 Rivalry: 🟢/🟡/🔴 — <量化证据一行>
- Force 2 New Entrants: 🟢/🟡/🔴 — <证据>
- Force 3 Substitutes: 🟢/🟡/🔴 — <证据>
- Force 4 Buyer Power: 🟢/🟡/🔴 — <证据>
- Force 5 Supplier Power: 🟢/🟡/🔴 — <证据>

## 3. 选股表 (capture-adjusted 排序)
<上述 D.1 (1) 表格>

## 4. 择赛道分
- 综合得分: <0-100>
- 跨赛道对比: <列其他已扫描赛道分数>

## 5. Anchors for /web3-vc:fundamental
<上述 D.2 块>

## 6. 数据卫生 + 局限
- Dune 数据时点: <timestamp>
- DefiLlama 数据时点: <timestamp>
- Phase B 跳过项: <列表，若有>
- 已知 schema-drift 风险: <SQL 模板中表名验证情况>

## 7. 可证伪的关键问题（指导后续监控）
- 看多本赛道 / 本赛道龙头协议的关键观察点：<具体指标 + 阈值>
- 看空触发：<具体指标 + 阈值>

> 本报告为赛道结构研究框架演示，非投资建议。
```

#### D.4 保存
写入 `./sectors/<sector>-<YYYY-MM-DD>.md`。若目录不存在，创建。

---

## 重要原则（贯穿全程）

1. **先明确赛道边界**——边界乱串数字会全错
2. **DefiLlama 管广度，Dune 管深度**——不要用 Dune 替代 DefiLlama 拉标准指标（浪费 credit + 重复工作）
3. **每个五力结论必须有量化证据一行**——不允许只给定性灯号
4. **HHI / take rate / share migration 三件套是赛道层的"血压心率"**——每次扫描必须出
5. **输出双视角**：选股表（rank by 真实捕获）+ 择赛道分（结构吸引力 0-100）
6. **必喂回 /fundamental 锚**：g 锚 + m 锚，让单点估值不再悬空
7. **Schema-drift 警告**：每个 Dune SQL 运行前必须用 `searchTables` 验证表名
8. **Credit 节约**：Phase B 每次 ~10 credits，不滥用；用户问"再 update 一下" 时若 <24h 内已跑过，直接复用已有结果

## Failure modes

- 用户给的赛道在 DefiLlama 不存在：先用 `list_protocols(category=X)` 试，空集就让用户重新指定
- Dune MCP 没配 / API key 失效：跳过 Phase B，明确标注，仍出 Phase A + C 部分输出
- SQL 模板里某个 Spellbook 表已被弃用：`searchTables` 找最新名，更新模板（写一行 PR 评论说明）
- 整个赛道只有 1-2 个协议（如某些新兴赛道）：HHI 没意义，跳过 Phase C 的 Force 1/2，只做单点深度
