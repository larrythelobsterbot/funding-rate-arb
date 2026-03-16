"""
LighterCaller — Fetch funding rates from Lighter (formerly Lighter.xyz).

API docs: https://docs.lighter.xyz/
Architecture: zkRollup CLOB on Ethereum L2

TODO Phase 2: implement full REST caller.
  - Endpoint TBD — Lighter may use WebSocket for real-time data.
  - Check docs for /v1/funding-rates or equivalent.
"""

import requests
from GlobalUtils.logger import logger


LIGHTER_BASE_URL = "https://api.lighter.xyz"


class LighterCaller:
    def __init__(self):
        self.session = requests.Session()

    def get_funding_rates(self, symbols: list) -> list:
        """
        Fetch funding rates from Lighter for the given symbols.

        Returns list of dicts:
            { symbol, exchange, funding_rate, skew_usd }
        """
        rates = []
        for symbol in symbols:
            try:
                normalized = symbol.upper().replace("USDT", "").replace("-SWAP", "")
                # TODO: replace with actual Lighter endpoint
                resp = self.session.get(
                    f"{LIGHTER_BASE_URL}/v1/funding-rate",
                    params={"market": f"{normalized}-USD"},
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                funding_rate = float(data.get("fundingRate", data.get("rate", 0)))

                rates.append({
                    "symbol": normalized,
                    "exchange": "Lighter",
                    "funding_rate": funding_rate,
                    "skew_usd": 0,
                })

            except Exception as e:
                logger.warning(f"LighterCaller - Error fetching rate for {symbol}: {e}")
                continue

        return rates
