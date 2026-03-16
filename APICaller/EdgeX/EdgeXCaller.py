"""
EdgeXCaller — Fetch funding rates from EdgeX DEX.

API docs: https://docs.edgex.exchange/
Funding rate endpoint (REST):
  GET https://api.edgex.exchange/api/v1/public/funding-rate?symbol={symbol}

TODO Phase 2: implement full caller with rate normalization.
"""

import requests
from GlobalUtils.logger import logger


EDGEX_BASE_URL = "https://api.edgex.exchange"


class EdgeXCaller:
    def __init__(self):
        self.session = requests.Session()

    def get_funding_rates(self, symbols: list) -> list:
        """
        Fetch funding rates from EdgeX for the given symbols.

        Returns list of dicts:
            { symbol, exchange, funding_rate, skew_usd }
        """
        rates = []
        for symbol in symbols:
            try:
                normalized = symbol.upper().replace("USDT", "").replace("-SWAP", "")
                resp = self.session.get(
                    f"{EDGEX_BASE_URL}/api/v1/public/funding-rate",
                    params={"symbol": f"{normalized}USDT"},
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()

                # TODO: adjust parsing once API shape is confirmed
                funding_rate = float(data.get("fundingRate", data.get("rate", 0)))

                rates.append({
                    "symbol": normalized,
                    "exchange": "EdgeX",
                    "funding_rate": funding_rate,
                    "skew_usd": 0,
                })

            except Exception as e:
                logger.warning(f"EdgeXCaller - Error fetching rate for {symbol}: {e}")
                continue

        return rates
