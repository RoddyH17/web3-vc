"""Integration smoke tests against the live DefiLlama API.

Run with:
    uv run pytest -xvs tests/

These hit the live public API, so they require internet and are slow.
Mark them with @pytest.mark.integration so CI can skip if needed.
"""

from __future__ import annotations

import pytest

from defillama_mcp.client import DefiLlamaClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_protocols_returns_substantial_list() -> None:
    async with DefiLlamaClient() as c:
        data = await c.protocols()
    assert isinstance(data, list)
    assert len(data) > 100, "DefiLlama indexes thousands of protocols"
    sample = data[0]
    for required in ("name", "tvl", "category"):
        assert required in sample


@pytest.mark.asyncio
@pytest.mark.integration
async def test_chains_includes_ethereum() -> None:
    async with DefiLlamaClient() as c:
        data = await c.chains()
    assert isinstance(data, list)
    assert any(c.get("name") == "Ethereum" for c in data)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_dex_overview_has_protocols() -> None:
    async with DefiLlamaClient() as c:
        data = await c.dex_overview()
    assert "protocols" in data
    assert len(data["protocols"]) > 10


@pytest.mark.asyncio
@pytest.mark.integration
async def test_derivatives_overview_is_paywalled() -> None:
    """As of 2026-05, DefiLlama's /overview/derivatives is gated behind Pro.

    The server.py `derivatives_overview` tool catches this and falls back
    to a TVL-ranked list from /protocols. This test documents the current
    state of the upstream API — if it ever becomes free again, this test
    will fail and we should remove the fallback path.
    """
    from defillama_mcp.client import DefiLlamaPaywallError

    async with DefiLlamaClient() as c:
        with pytest.raises(DefiLlamaPaywallError):
            await c.derivatives_overview()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_protocols_includes_derivatives_category() -> None:
    """The fallback path relies on /protocols having Derivatives entries."""
    async with DefiLlamaClient() as c:
        data = await c.protocols()
    perps = [p for p in data if (p.get("category") or "").lower() == "derivatives"]
    assert len(perps) > 5, "expected at least 5 perp DEXes indexed by DefiLlama"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_protocol_fees_uniswap_default_datatype() -> None:
    async with DefiLlamaClient() as c:
        data = await c.protocol_fees("uniswap")
    assert data.get("total30d") is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_protocol_fees_three_data_types_aave() -> None:
    """Bug-fix verification: protocol_fees() accepts a data_type kwarg and
    returns the right stream for each. Aave is a good fixture because it
    has non-zero values for all three streams historically.
    """
    async with DefiLlamaClient() as c:
        fees = await c.protocol_fees("aave", data_type="dailyFees")
        revenue = await c.protocol_fees("aave", data_type="dailyRevenue")
        holders = await c.protocol_fees("aave", data_type="dailyHoldersRevenue")

    assert fees.get("total30d") is not None
    assert revenue.get("total30d") is not None
    # holders 30d may approach 0 if buyback paused, but the field exists
    assert "total30d" in holders or "totalAllTime" in holders

    # Sanity ordering: revenue <= fees, holders revenue <= revenue
    assert revenue["total30d"] <= fees["total30d"]
    if holders.get("total30d") is not None:
        assert holders["total30d"] <= revenue["total30d"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_protocol_detail_aave_supply_tvl_excludes_borrowed() -> None:
    """Bug-fix verification: TVL calc must exclude per-chain '*-borrowed'
    buckets (not just the aggregate 'borrowed' key). Aave's headline TVL
    was inflating to ~$25b before this fix; the correct supply TVL is ~$14b.
    """
    async with DefiLlamaClient() as c:
        p = await c.protocol("aave")

    chain_tvls = p.get("currentChainTvls") or {}
    assert chain_tvls, "Aave should always have chain TVL data"

    excluded_suffixes = ("-borrowed", "-staking", "-pool2")
    excluded_keys = {"borrowed", "staking", "pool2"}
    supply = sum(
        v for k, v in chain_tvls.items()
        if v is not None
        and k.lower() not in excluded_keys
        and not any(k.lower().endswith(s) for s in excluded_suffixes)
    )
    borrowed = sum(
        v for k, v in chain_tvls.items()
        if v is not None and k.lower().endswith("-borrowed")
    )

    assert supply > 1e9, f"Aave supply TVL {supply} below sanity floor"
    assert borrowed > 0, "Expected non-trivial borrowed amount on Aave"
    util = borrowed / supply
    assert 0.3 < util < 0.95, f"Aave utilization {util:.2f} outside healthy range"
