"""
HyperliquidCaller — Fetch funding rates from Hyperliquid L1.

API docs: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api
Endpoint:  POST https://api.hyperliquid.xyz/info
           body: {"type": "metaAndAssetCtxs"}

Returns: [meta, assetCtxs[]] where each assetCtx has:
  - funding: current 8h funding rate (string, e.g. "0.00012")
  - openInterest, midPx, markPx, etc.

SDK alternative: pip install hyperliquid-python-sdk
"""

import requests
from GlobalUtils.logger import logger


HYPERLIQUID_INFO_URL = "https://api.hyperliquid.xyz/info"


class HyperliquidCaller:
    def __init__(self):
        self.session = requests.Session()

    def get_funding_rates(self, symbols: list) -> list:
        """
        Fetch funding rates from Hyperliquid for the given symbols.

        Returns list of dicts:
            { symbol, exchange, funding_rate, skew_usd }
        """
        try:
            resp = self.session.post(
                HYPERLIQUID_INFO_URL,
                json={"type": "metaAndAssetCtxs"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list) or len(data) < 2:
                logger.error("HyperliquidCaller - Unexpected response shape")
                return []

            meta = data[0]
            asset_ctxs = data[1]
            universe = meta.get("universe", [])

            # Build name→index map
            name_map = {}
            for i, asset in enumerate(universe):
                name_map[asset["name"].upper()] = i

            # Normalize requested symbols
            normalized = [s.upper().replace("USDT", "").replace("-SWAP", "") for s in symbols]

            rates = []
            for sym in normalized:
                idx = name_map.get(sym)
                if idx is None or idx >= len(asset_ctxs):
                    continue
                ctx = asset_ctxs[idx]
                funding_8h = float(ctx.get("funding", "0"))
                open_interest = float(ctx.get("openInterest", "0"))
                mark_price = float(ctx.get("markPx", "0"))
                oi_usd = open_interest * mark_price

                rates.append({
                    "symbol": sym,
                    "exchange": "Hyperliquid",
                    "funding_rate": funding_8h,
                    "skew_usd": 0,  # Hyperliquid doesn't expose skew directly
                })

            return rates

        except Exception as e:
            logger.error(f"HyperliquidCaller - Error fetching funding rates: {e}")
            return []

    def get_mark_price(self, symbol: str) -> float:
        """Get current mark price for a symbol."""
        try:
            resp = self.session.post(
                HYPERLIQUID_INFO_URL,
                json={"type": "metaAndAssetCtxs"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            meta = data[0]
            asset_ctxs = data[1]
            universe = meta.get("universe", [])

            for i, asset in enumerate(universe):
                if asset["name"].upper() == symbol.upper():
                    return float(asset_ctxs[i].get("markPx", 0))
            return 0
        except Exception as e:
            logger.error(f"HyperliquidCaller - Error fetching mark price for {symbol}: {e}")
            return 0
