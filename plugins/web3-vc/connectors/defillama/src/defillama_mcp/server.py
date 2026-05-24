"""MCP server exposing DefiLlama tools for the web3-vc plugin.

Run with:
    uv run python -m defillama_mcp.server

Or via the script entry point:
    uv run defillama-mcp
"""

from __future__ import annotations

from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from defillama_mcp.client import DefiLlamaClient, DefiLlamaPaywallError

mcp = FastMCP("defillama")


# ---- formatting helpers -----------------------------------------


def _fmt_money(v: float | int | None) -> str:
    if v is None:
        return "n/a"
    v = float(v)
    abs_v = abs(v)
    if abs_v >= 1e9:
        return f"${v / 1e9:.2f}b"
    if abs_v >= 1e6:
        return f"${v / 1e6:.2f}m"
    if abs_v >= 1e3:
        return f"${v / 1e3:.2f}k"
    return f"${v:.2f}"


def _fmt_pct(v: float | int | None) -> str:
    if v is None:
        return "n/a"
    return f"{float(v):+.2f}%"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---- tools ------------------------------------------------------


@mcp.tool()
async def list_protocols(
    category: str | None = None,
    chain: str | None = None,
    top_n: int = 20,
) -> str:
    """List top DeFi protocols by TVL.

    Filter by `category` (e.g. "Dexs", "Derivatives", "Lending", "Yield",
    "RWA", "Liquid Staking") or `chain` (e.g. "Ethereum", "Solana", "Base").
    Note: DefiLlama category names are case-sensitive and use specific
    spellings — if a filter returns empty, try variants.
    """
    async with DefiLlamaClient() as client:
        data = await client.protocols()

    if category:
        cat_lower = category.lower()
        data = [p for p in data if (p.get("category") or "").lower() == cat_lower]
    if chain:
        chain_lower = chain.lower()
        data = [
            p
            for p in data
            if chain_lower in [c.lower() for c in (p.get("chains") or [])]
        ]

    data.sort(key=lambda p: p.get("tvl") or 0, reverse=True)
    top = data[: max(1, top_n)]

    header_bits = []
    if category:
        header_bits.append(f"category: {category}")
    if chain:
        header_bits.append(f"chain: {chain}")
    header_suffix = f" ({', '.join(header_bits)})" if header_bits else ""

    lines = [
        f"# Top {len(top)} protocols by TVL{header_suffix}",
        f"_Pulled {_timestamp()} from DefiLlama_",
        "",
        "| Rank | Protocol | Slug | Category | TVL | 1d Δ | 7d Δ | 30d Δ | Chains |",
        "|---:|---|---|---|---:|---:|---:|---:|---|",
    ]
    for i, p in enumerate(top, 1):
        chains = p.get("chains") or []
        chain_str = ", ".join(chains[:4]) or "—"
        if len(chains) > 4:
            chain_str += f" (+{len(chains) - 4})"
        lines.append(
            f"| {i} | {p.get('name', '?')} | `{p.get('slug', '?')}` | "
            f"{p.get('category', '—')} | {_fmt_money(p.get('tvl'))} | "
            f"{_fmt_pct(p.get('change_1d'))} | {_fmt_pct(p.get('change_7d'))} | "
            f"{_fmt_pct(p.get('change_1m'))} | {chain_str} |"
        )
    if len(data) > len(top):
        lines.extend(["", f"_Showing top {len(top)} of {len(data)} matching protocols._"])
    if not top:
        lines.append("")
        lines.append("_No protocols matched. Check category / chain spelling (DefiLlama is case-sensitive)._")
    return "\n".join(lines)


def _bucket_kind(key: str) -> str:
    """Classify a DefiLlama currentChainTvls bucket key.

    DefiLlama returns buckets like:
      "Ethereum"            -> supply on Ethereum
      "Ethereum-borrowed"   -> borrowed on Ethereum (NOT to count as TVL)
      "Ethereum-staking"    -> staking module on Ethereum
      "borrowed"            -> aggregate borrowed across all chains
      "staking"             -> aggregate staking across all chains
      "pool2"               -> LP-token incentives bucket

    The per-chain `-borrowed` / `-staking` / `-pool2` buckets are subsets
    of the aggregate keys; summing both double-counts. Earlier code only
    excluded the aggregate keys (`borrowed`) and missed per-chain
    (`Ethereum-borrowed`), so for lending protocols like Aave the headline
    "TVL" was inflated by ~$11b.
    """
    k = key.lower()
    if k in ("borrowed", "staking", "pool2"):
        return k
    for suffix in ("-borrowed", "-staking", "-pool2"):
        if k.endswith(suffix):
            return suffix.lstrip("-")
    return "supply"


@mcp.tool()
async def protocol_detail(slug: str) -> str:
    """Detailed data for a single protocol by slug.

    Returns name, category, chains, TVL breakdown correctly separated
    into supply / borrowed / staking, plus token metadata.

    For lending protocols, **Supply TVL** (deposits) is the right
    denominator for capital-efficiency ratios. Borrowed should NOT be
    added — it is sourced from the supply side and double-counts.
    """
    async with DefiLlamaClient() as client:
        p = await client.protocol(slug)

    chain_tvls = p.get("currentChainTvls") or {}

    by_chain_supply: dict[str, float] = {}
    by_chain_borrowed: dict[str, float] = {}
    staking_total = 0.0
    pool2_total = 0.0
    agg_borrowed = 0.0
    for k, v in chain_tvls.items():
        if v is None:
            continue
        kind = _bucket_kind(k)
        if kind == "supply":
            by_chain_supply[k] = float(v)
        elif kind == "borrowed":
            if k.lower() == "borrowed":
                agg_borrowed = float(v)
            else:
                chain = k.rsplit("-borrowed", 1)[0]
                by_chain_borrowed[chain] = float(v)
        elif kind == "staking":
            if k.lower() == "staking":
                staking_total = max(staking_total, float(v))
        elif kind == "pool2":
            if k.lower() == "pool2":
                pool2_total = max(pool2_total, float(v))

    supply_total = sum(by_chain_supply.values())
    borrowed_total = sum(by_chain_borrowed.values()) or agg_borrowed
    net_liquidity = supply_total - borrowed_total
    utilization = (borrowed_total / supply_total * 100) if supply_total > 0 else None

    audit_raw = p.get("audit_links")
    if isinstance(audit_raw, list):
        audit_str = ", ".join(audit_raw) if audit_raw else "—"
    else:
        audit_str = str(audit_raw) if audit_raw else "—"

    lines = [
        f"# {p.get('name', slug)}",
        f"_Pulled {_timestamp()} from DefiLlama_",
        "",
        f"- **Slug**: `{p.get('id', slug)}`",
        f"- **Category**: {p.get('category') or '—'}",
        f"- **Chains**: {', '.join(p.get('chains', []) or ['—'])}",
        f"- **Token**: {p.get('symbol') or '—'}",
        f"- **URL**: {p.get('url') or '—'}",
        f"- **Twitter**: {p.get('twitter') or '—'}",
        f"- **gecko_id**: {p.get('gecko_id') or '—'}",
        f"- **Market Cap (DefiLlama)**: {_fmt_money(p.get('mcap'))}",
        f"- **FDV (DefiLlama, often null — cross-check CoinGecko)**: {_fmt_money(p.get('fdv'))}",
        f"- **Audit links**: {audit_str}",
        "",
        "## TVL breakdown (correct accounting)",
        "",
        f"- **Supply (deposits) TVL**: {_fmt_money(supply_total)} — use as denominator for capital-efficiency ratios",
        f"- **Borrowed**: {_fmt_money(borrowed_total)} — already in supply; do NOT add to TVL",
        f"- **Net liquidity (Supply − Borrowed)**: {_fmt_money(net_liquidity)}",
    ]
    if utilization is not None:
        lines.append(f"- **Utilization** (Borrowed / Supply): {utilization:.1f}%")
    if staking_total > 0:
        lines.append(f"- **Staking module TVL**: {_fmt_money(staking_total)} — separate pool")
    if pool2_total > 0:
        lines.append(f"- **Pool2 (incentive) TVL**: {_fmt_money(pool2_total)}")

    lines += [
        "",
        "## Description",
        p.get("description") or "_No description._",
        "",
        "## Supply TVL by chain (with per-chain utilization)",
    ]
    if by_chain_supply:
        lines.append("| Chain | Supply | Borrowed | Utilization |")
        lines.append("|---|---:|---:|---:|")
        for chain in sorted(by_chain_supply.keys(), key=lambda c: -by_chain_supply[c]):
            sup = by_chain_supply[chain]
            bor = by_chain_borrowed.get(chain, 0.0)
            util = (bor / sup * 100) if sup > 0 else 0.0
            lines.append(f"| {chain} | {_fmt_money(sup)} | {_fmt_money(bor)} | {util:.0f}% |")
    else:
        lines.append("_No chain breakdown available._")
    return "\n".join(lines)


@mcp.tool()
async def protocol_fees(slug: str) -> str:
    """Fees, revenue, AND holders revenue for a single protocol.

    Calls three DefiLlama dataType endpoints (`dailyFees`, `dailyRevenue`,
    `dailyHoldersRevenue`) and combines them into one report covering:

    - **Fees**: total dollars paid by users (covers all stakeholders)
    - **Revenue**: portion accruing to the protocol (after LP/supplier cut)
    - **Holders Revenue**: portion actually flowing to token holders —
      THE "value capture bridge" metric. Usually 0 if no fee switch /
      buyback / staking distribution.

    Computes two key ratios:
    - **Take rate** = Revenue / Fees (how much the protocol keeps)
    - **Holder capture rate** = Holders Revenue / Revenue (THE bridge —
      how much actually reaches token holders)

    Reports each stream as 24h/7d/30d/all-time so trend changes (e.g.,
    buyback program kicked in mid-month) are visible.
    """
    async def _try(client: DefiLlamaClient, data_type: str) -> dict | None:
        try:
            return await client.protocol_fees(slug, data_type=data_type)
        except DefiLlamaError:
            return None

    async with DefiLlamaClient() as client:
        fees = await _try(client, "dailyFees")
        if fees is None:
            return f"# {slug} — fees\n\n_Not indexed by DefiLlama fees adapter._"
        revenue = await _try(client, "dailyRevenue")
        holders = await _try(client, "dailyHoldersRevenue")

    def _vals(d: dict | None, window: str) -> float | None:
        if d is None:
            return None
        v = d.get(f"total{window}")
        return float(v) if v is not None else None

    fees_30d = _vals(fees, "30d")
    rev_30d = _vals(revenue, "30d")
    hr_30d = _vals(holders, "30d")
    rev_all = _vals(revenue, "AllTime")
    hr_all = _vals(holders, "AllTime")

    take_rate = (rev_30d / fees_30d * 100) if (fees_30d and rev_30d is not None) else None
    holder_capture = (hr_30d / rev_30d * 100) if (rev_30d and hr_30d is not None) else None
    holder_capture_lifetime = (hr_all / rev_all * 100) if (rev_all and hr_all is not None) else None

    annualized_fees = fees_30d * 12 if fees_30d is not None else None
    annualized_rev = rev_30d * 12 if rev_30d is not None else None
    annualized_hr = hr_30d * 12 if hr_30d is not None else None

    def _row(label: str, d: dict | None) -> str:
        return (
            f"| {label} | "
            f"{_fmt_money(_vals(d, '24h'))} | "
            f"{_fmt_money(_vals(d, '7d'))} | "
            f"{_fmt_money(_vals(d, '30d'))} | "
            f"{_fmt_money(_vals(d, 'AllTime'))} |"
        )

    lines = [
        f"# {fees.get('name', slug)} — fees, revenue & holders revenue",
        f"_Pulled {_timestamp()} from DefiLlama_",
        "",
        f"- **Category**: {fees.get('category') or '—'}",
        f"- **Chains**: {', '.join(fees.get('chains', []) or ['—'])}",
        "",
        "## Three dollar streams",
        "",
        "| Stream | 24h | 7d | 30d | All-time |",
        "|---|---:|---:|---:|---:|",
        _row("Fees (paid by users)", fees),
        _row("Revenue (protocol take)", revenue),
        _row("Holders Revenue (token take)", holders),
        "",
        "## Annualized run-rate (30d × 12)",
        "",
        f"- **Annual Fees**: {_fmt_money(annualized_fees)}",
        f"- **Annual Revenue**: {_fmt_money(annualized_rev)}",
        f"- **Annual Holders Revenue**: {_fmt_money(annualized_hr)}",
        "",
        "## Bridge ratios (the value-capture chain)",
        "",
    ]
    if take_rate is not None:
        lines.append(f"- **Take rate (30d)** = Revenue / Fees = **{take_rate:.2f}%**")
    else:
        lines.append("- **Take rate (30d)**: n/a (missing data)")

    if holder_capture is not None:
        flag = " ⚠️ bridge near-broken" if holder_capture < 1 else ""
        lines.append(
            f"- **Holder capture rate (30d)** = Holders Rev / Revenue = **{holder_capture:.2f}%**{flag}"
        )
    else:
        lines.append("- **Holder capture rate (30d)**: n/a (holders revenue not indexed or zero)")

    if holder_capture_lifetime is not None and holder_capture is not None:
        delta = holder_capture - holder_capture_lifetime
        trend = "↑ widening" if delta > 0.5 else ("↓ narrowing" if delta < -0.5 else "≈ stable")
        lines.append(
            f"- **Holder capture (lifetime)**: {holder_capture_lifetime:.2f}% — "
            f"current vs lifetime: **{trend}** ({delta:+.2f}pp)"
        )

    lines += [
        "",
        "> **Reading guide:**",
        "> - Take rate near 0%: protocol gives everything to LPs/suppliers (e.g. Uniswap V3 default).",
        "> - Holder capture near 0%: revenue exists but doesn't reach token holders — fee switch off / no buyback.",
        "> - Lifetime > current capture: bridge was wider historically (e.g. buyback paused).",
    ]
    return "\n".join(lines)


@mcp.tool()
async def dex_overview(top_n: int = 20) -> str:
    """Spot DEX volume overview — top protocols by 7d volume."""
    async with DefiLlamaClient() as client:
        data = await client.dex_overview()

    protocols = data.get("protocols") or []
    protocols.sort(key=lambda p: p.get("total7d") or 0, reverse=True)
    top = protocols[: max(1, top_n)]

    lines = [
        f"# Spot DEX overview — top {len(top)} by 7d volume",
        f"_Pulled {_timestamp()} from DefiLlama_",
        "",
        f"**Total DEX volume:** 7d {_fmt_money(data.get('total7d'))} | 30d {_fmt_money(data.get('total30d'))}",
        "",
        "| Rank | DEX | 24h vol | 7d vol | 30d vol | 7d Δ | 30d Δ | Chains |",
        "|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for i, p in enumerate(top, 1):
        chains = ", ".join((p.get("chains") or [])[:3]) or "—"
        lines.append(
            f"| {i} | {p.get('name', '?')} | "
            f"{_fmt_money(p.get('total24h'))} | "
            f"{_fmt_money(p.get('total7d'))} | "
            f"{_fmt_money(p.get('total30d'))} | "
            f"{_fmt_pct(p.get('change_7d'))} | "
            f"{_fmt_pct(p.get('change_1m'))} | "
            f"{chains} |"
        )
    return "\n".join(lines)


@mcp.tool()
async def derivatives_overview(top_n: int = 20) -> str:
    """Perpetual / derivatives DEX overview.

    Tries the volume-aggregate endpoint first (Pro tier — currently 402 for
    free users). Falls back to a TVL-ranked perp DEX list from `/protocols`,
    which is free. The fallback omits volume / fees per protocol — for
    those, run `protocol_dex` or `protocol_fees` per slug.
    """
    async with DefiLlamaClient() as client:
        try:
            data = await client.derivatives_overview()
        except DefiLlamaPaywallError:
            # Fall back to TVL-ranked perp DEX list from the free /protocols endpoint.
            all_p = await client.protocols()
            perps = [p for p in all_p if (p.get("category") or "").lower() == "derivatives"]
            perps.sort(key=lambda p: p.get("tvl") or 0, reverse=True)
            top = perps[: max(1, top_n)]
            lines = [
                f"# Derivatives (Perp) DEX overview — top {len(top)} by TVL  *(fallback view)*",
                f"_Pulled {_timestamp()} from DefiLlama_",
                "",
                "> **Note:** DefiLlama's `/overview/derivatives` volume endpoint is gated behind the Pro tier (402). ",
                "> This fallback ranks perp DEXes by TVL instead of volume. For per-protocol volume / fees, ",
                "> call `protocol_dex(slug)` or `protocol_fees(slug)` individually.",
                "",
                "| Rank | Protocol | Slug | TVL | 1d Δ | 7d Δ | 30d Δ | Chains |",
                "|---:|---|---|---:|---:|---:|---:|---|",
            ]
            for i, p in enumerate(top, 1):
                chains = ", ".join((p.get("chains") or [])[:3]) or "—"
                lines.append(
                    f"| {i} | {p.get('name', '?')} | `{p.get('slug', '?')}` | "
                    f"{_fmt_money(p.get('tvl'))} | "
                    f"{_fmt_pct(p.get('change_1d'))} | "
                    f"{_fmt_pct(p.get('change_7d'))} | "
                    f"{_fmt_pct(p.get('change_1m'))} | "
                    f"{chains} |"
                )
            return "\n".join(lines)

    protocols = data.get("protocols") or []
    protocols.sort(key=lambda p: p.get("total7d") or 0, reverse=True)
    top = protocols[: max(1, top_n)]

    lines = [
        f"# Derivatives (Perp) DEX overview — top {len(top)} by 7d volume",
        f"_Pulled {_timestamp()} from DefiLlama_",
        "",
        f"**Total perp DEX volume:** 7d {_fmt_money(data.get('total7d'))} | 30d {_fmt_money(data.get('total30d'))}",
        "",
        "| Rank | Protocol | 24h vol | 7d vol | 30d vol | 7d Δ | 30d Δ | Chains |",
        "|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for i, p in enumerate(top, 1):
        chains = ", ".join((p.get("chains") or [])[:3]) or "—"
        lines.append(
            f"| {i} | {p.get('name', '?')} | "
            f"{_fmt_money(p.get('total24h'))} | "
            f"{_fmt_money(p.get('total7d'))} | "
            f"{_fmt_money(p.get('total30d'))} | "
            f"{_fmt_pct(p.get('change_7d'))} | "
            f"{_fmt_pct(p.get('change_1m'))} | "
            f"{chains} |"
        )
    return "\n".join(lines)


@mcp.tool()
async def fees_overview(top_n: int = 20) -> str:
    """Fees and revenue overview across all indexed protocols — top by 7d fees."""
    async with DefiLlamaClient() as client:
        data = await client.fees_overview()

    protocols = data.get("protocols") or []
    protocols.sort(key=lambda p: p.get("total7d") or 0, reverse=True)
    top = protocols[: max(1, top_n)]

    lines = [
        f"# Fees overview — top {len(top)} protocols by 7d fees",
        f"_Pulled {_timestamp()} from DefiLlama_",
        "",
        "| Rank | Protocol | Category | 24h fees | 7d fees | 30d fees | 7d Rev | 30d Rev |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for i, p in enumerate(top, 1):
        lines.append(
            f"| {i} | {p.get('name', '?')} | "
            f"{p.get('category', '—')} | "
            f"{_fmt_money(p.get('total24h'))} | "
            f"{_fmt_money(p.get('total7d'))} | "
            f"{_fmt_money(p.get('total30d'))} | "
            f"{_fmt_money(p.get('totalRevenue7d'))} | "
            f"{_fmt_money(p.get('totalRevenue30d'))} |"
        )
    return "\n".join(lines)


@mcp.tool()
async def list_chains(top_n: int = 20) -> str:
    """Top chains by total TVL."""
    async with DefiLlamaClient() as client:
        data = await client.chains()

    data.sort(key=lambda c: c.get("tvl") or 0, reverse=True)
    top = data[: max(1, top_n)]

    lines = [
        f"# Top {len(top)} chains by TVL",
        f"_Pulled {_timestamp()} from DefiLlama_",
        "",
        "| Rank | Chain | TVL | Native token |",
        "|---:|---|---:|---|",
    ]
    for i, c in enumerate(top, 1):
        lines.append(
            f"| {i} | {c.get('name', '?')} | "
            f"{_fmt_money(c.get('tvl'))} | "
            f"{c.get('tokenSymbol', '—')} |"
        )
    return "\n".join(lines)


def main() -> None:
    """Entry point for `python -m defillama_mcp.server` and the script."""
    mcp.run()


if __name__ == "__main__":
    main()
