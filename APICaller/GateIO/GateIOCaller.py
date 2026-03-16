"""
GateIOCaller — Fetch funding rates from Gate.io futures.

API docs: https://www.gate.io/docs/developers/apiv4/en/
Endpoint:
  GET https://api.gateio.ws/api/v4/futures/usdt/contracts/{contract}
    → includes funding_rate, funding_next_apply, mark_price

SDK alternative: pip install gate-api
"""

import requests
from GlobalUtils.logger import logger


GATEIO_BASE_URL = "https://api.gateio.ws/api/v4"


class GateIOCaller:
    def __init__(self):
        self.session = requests.Session()

    def get_funding_rates(self, symbols: list) -> list:
        """
        Fetch funding rates from Gate.io for the given symbols.

        Gate.io contract format: BTC_USDT, ETH_USDT, etc.

        Returns list of dicts:
            { symbol, exchange, funding_rate, skew_usd }
        """
        rates = []
        for symbol in symbols:
            try:
                normalized = symbol.upper().replace("USDT", "").replace("-SWAP", "")
                contract = f"{normalized}_USDT"

                resp = self.session.get(
                    f"{GATEIO_BASE_URL}/futures/usdt/contracts/{contract}",
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()

                # Gate.io returns funding_rate as a string decimal
                funding_rate_raw = float(data.get("funding_rate", "0"))
                # Gate.io rates are 8-hour rates already
                funding_rate_8h = funding_rate_raw

                rates.append({
                    "symbol": normalized,
                    "exchange": "GateIO",
                    "funding_rate": funding_rate_8h,
                    "skew_usd": 0,
                })

            except Exception as e:
                logger.warning(f"GateIOCaller - Error fetching rate for {symbol}: {e}")
                continue

        return rates
