"""Async HTTP client for the DefiLlama public API.

DefiLlama is a free public service — no auth required. We keep the client
deliberately thin (no caching, no rate limiting) so behavior is predictable
and the MCP server layer can decide formatting / retry policy.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

BASE_TVL = "https://api.llama.fi"
BASE_STABLECOINS = "https://stablecoins.llama.fi"

DEFAULT_TIMEOUT = 30.0
USER_AGENT = "web3-vc-plugin/0.1.0 (DefiLlama MCP connector)"


class DefiLlamaError(RuntimeError):
    """Raised when a DefiLlama fetch fails after retries."""


class DefiLlamaPaywallError(DefiLlamaError):
    """Raised when an endpoint returns 402 — gated behind the Pro tier.

    Currently affects `/overview/derivatives` (perp DEX volume aggregate).
    Free alternatives exist for most other use cases; see server.py
    fallbacks.
    """


class DefiLlamaClient:
    """Thin async wrapper around DefiLlama public endpoints.

    Retries once with a 2-second backoff on 5xx or network errors. Surfaces
    a clear error if the second attempt fails — the MCP server layer is
    responsible for telling the user what to do next.
    """

    def __init__(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "DefiLlamaClient":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def _get(self, url: str, params: dict | None = None) -> Any:
        for attempt in range(2):
            try:
                resp = await self._client.get(url, params=params)
                if resp.status_code == 402:
                    raise DefiLlamaPaywallError(f"402 (Pro tier required) for {url}")
                if resp.status_code >= 500 and attempt == 0:
                    await asyncio.sleep(2.0)
                    continue
                resp.raise_for_status()
                return resp.json()
            except (httpx.TimeoutException, httpx.NetworkError):
                if attempt == 0:
                    await asyncio.sleep(2.0)
                    continue
                raise DefiLlamaError(f"Network error fetching {url}")
            except httpx.HTTPStatusError as e:
                raise DefiLlamaError(f"{e.response.status_code} from {url}: {e.response.text[:200]}")
        raise DefiLlamaError(f"persistent 5xx from {url}")

    # ---- endpoints ------------------------------------------------

    async def protocols(self) -> list[dict]:
        """All protocols indexed by DefiLlama (returns full list, ~3000+)."""
        return await self._get(f"{BASE_TVL}/protocols")

    async def protocol(self, slug: str) -> dict:
        """Full protocol detail including TVL history and chain breakdown."""
        return await self._get(f"{BASE_TVL}/protocol/{slug}")

    async def chains(self) -> list[dict]:
        """All chains tracked by DefiLlama."""
        return await self._get(f"{BASE_TVL}/v2/chains")

    async def dex_overview(self, exclude_charts: bool = True) -> dict:
        """Spot DEX volume overview across all DEX protocols."""
        params: dict = {}
        if exclude_charts:
            params["excludeTotalDataChart"] = "true"
            params["excludeTotalDataChartBreakdown"] = "true"
        return await self._get(f"{BASE_TVL}/overview/dexs", params=params)

    async def derivatives_overview(self, exclude_charts: bool = True) -> dict:
        """Perpetual / derivatives DEX overview."""
        params: dict = {}
        if exclude_charts:
            params["excludeTotalDataChart"] = "true"
            params["excludeTotalDataChartBreakdown"] = "true"
        return await self._get(f"{BASE_TVL}/overview/derivatives", params=params)

    async def fees_overview(self, exclude_charts: bool = True) -> dict:
        """Fees and revenue overview across all indexed protocols."""
        params: dict = {}
        if exclude_charts:
            params["excludeTotalDataChart"] = "true"
            params["excludeTotalDataChartBreakdown"] = "true"
        return await self._get(f"{BASE_TVL}/overview/fees", params=params)

    async def protocol_fees(self, slug: str, data_type: str = "dailyFees") -> dict:
        """Fees / revenue / holders-revenue summary for a single protocol.

        `data_type` selects which dollar stream the endpoint returns under
        the `total24h/7d/30d/AllTime` keys. DefiLlama supports:

        - `dailyFees` — total fees paid by users (default)
        - `dailyRevenue` — portion accruing to the protocol (after LP cut)
        - `dailyHoldersRevenue` — portion accruing to token holders (THE
          "value capture bridge" metric — usually 0 if no fee switch /
          buyback / staking distribution)
        - `dailySupplySideRevenue` — portion accruing to LPs/suppliers
        """
        return await self._get(
            f"{BASE_TVL}/summary/fees/{slug}",
            params={"dataType": data_type},
        )

    async def protocol_dex(self, slug: str) -> dict:
        """Volume detail for a single DEX protocol."""
        return await self._get(f"{BASE_TVL}/summary/dexs/{slug}")

    async def stablecoins(self) -> dict:
        """Stablecoin supply overview."""
        return await self._get(f"{BASE_STABLECOINS}/stablecoins")
