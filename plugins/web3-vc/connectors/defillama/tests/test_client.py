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
async def test_protocol_fees_uniswap() -> None:
    async with DefiLlamaClient() as c:
        data = await c.protocol_fees("uniswap")
    assert data.get("total30d") is not None
