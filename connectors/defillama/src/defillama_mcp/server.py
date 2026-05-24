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


@mcp.tool()
async def protocol_detail(slug: str) -> str:
    """Detailed data for a single protocol by slug.

    Returns name, category, chains, current TVL with chain breakdown,
    description, official URL, token symbol, Twitter, and audit links.
    """
    async with DefiLlamaClient() as client:
        p = await client.protocol(slug)

    chain_tvls = p.get("currentChainTvls") or {}
    # Sum "real" TVL excluding staking / pool2 / borrowed (which inflate the headline).
    tvl_now = sum(
        v for k, v in chain_tvls.items()
        if not any(k.lower().startswith(prefix) for prefix in ("staking", "pool2", "borrowed"))
    ) if chain_tvls else None

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
        f"- **Category**: {p.get('category', '—')}",
        f"- **Chains**: {', '.join(p.get('chains', []) or ['—'])}",
        f"- **Current TVL** (ex. staking/pool2/borrowed): {_fmt_money(tvl_now)}",
        f"- **Token**: {p.get('symbol', '—')}",
        f"- **URL**: {p.get('url', '—')}",
        f"- **Twitter**: {p.get('twitter', '—')}",
        f"- **Audit links**: {audit_str}",
        "",
        f"## Description",
        p.get("description") or "_No description._",
        "",
        "## TVL by chain (current, all categories)",
    ]
    if chain_tvls:
        lines.append("| Chain bucket | TVL |")
        lines.append("|---|---:|")
        for k, v in sorted(chain_tvls.items(), key=lambda kv: -(kv[1] or 0)):
            lines.append(f"| {k} | {_fmt_money(v)} |")
    else:
        lines.append("_No chain breakdown available._")
    return "\n".join(lines)


@mcp.tool()
async def protocol_fees(slug: str) -> str:
    """Fees and revenue for a single protocol.

    Returns 24h / 7d / 30d fees and revenue, plus the take rate
    (revenue / fees). Reports 'not indexed' if the protocol is not in
    DefiLlama's fee adapter set.
    """
    async with DefiLlamaClient() as client:
        try:
            f = await client.protocol_fees(slug)
        except Exception as e:
            return (
                f"# {slug} — fees\n\n"
                f"_Not indexed by DefiLlama fees adapter, or fetch failed: {e}_"
            )

    fees_30d_raw = f.get("total30d")
    rev_30d_raw = f.get("totalRevenue30d")
    # Only compute take rate when BOTH numbers are present — otherwise show n/a.
    if fees_30d_raw and rev_30d_raw is not None:
        take_rate: float | None = (rev_30d_raw / fees_30d_raw * 100)
    else:
        take_rate = None

    lines = [
        f"# {f.get('name', slug)} — fees & revenue",
        f"_Pulled {_timestamp()} from DefiLlama_",
        "",
        f"- **Category**: {f.get('category') or '—'}",
        f"- **Chains**: {', '.join(f.get('chains', []) or ['—'])}",
        "",
        "## Fees",
        f"- 24h: {_fmt_money(f.get('total24h'))}",
        f"- 7d:  {_fmt_money(f.get('total7d'))}",
        f"- 30d: {_fmt_money(f.get('total30d'))}",
        "",
        "## Revenue (protocol / token take)",
        f"- 24h: {_fmt_money(f.get('totalRevenue24h'))}",
        f"- 7d:  {_fmt_money(f.get('totalRevenue7d'))}",
        f"- 30d: {_fmt_money(f.get('totalRevenue30d'))}",
    ]
    if take_rate is not None:
        lines.extend(["", f"- **Take rate (30d, revenue/fees)**: {take_rate:.1f}%"])
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
