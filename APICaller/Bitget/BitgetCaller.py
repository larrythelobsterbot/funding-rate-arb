"""
BitgetCaller — Fetch funding rates from Bitget futures.

API docs: https://www.bitget.com/api-doc/contract/market/Get-Current-Funding-Rate
Endpoint:
  GET https://api.bitget.com/api/v2/mix/market/current-fund-rate?symbol={symbol}&productType=USDT-FUTURES
    → { "data": [{ "symbol": "BTCUSDT", "fundingRate": "0.0001" }] }

Funding rates are 8-hour by default.
"""

import requests
from GlobalUtils.logger import logger


BITGET_BASE_URL = "https://api.bitget.com/api/v2"


class BitgetCaller:
    def __init__(self):
        self.session = requests.Session()

    def get_funding_rates(self, symbols: list) -> list:
        """
        Fetch funding rates from Bitget for the given symbols.

        Returns list of dicts:
            { symbol, exchange, funding_rate, skew_usd }
        """
        rates = []
        for symbol in symbols:
            try:
                normalized = symbol.upper().replace("USDT", "").replace("-SWAP", "")
                bitget_symbol = f"{normalized}USDT"

                resp = self.session.get(
                    f"{BITGET_BASE_URL}/mix/market/current-fund-rate",
                    params={
                        "symbol": bitget_symbol,
                        "productType": "USDT-FUTURES",
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()

                fund_data = data.get("data", [])
                if fund_data and len(fund_data) > 0:
                    funding_rate_8h = float(fund_data[0].get("fundingRate", "0"))
                else:
                    funding_rate_8h = 0

                rates.append({
                    "symbol": normalized,
                    "exchange": "Bitget",
                    "funding_rate": funding_rate_8h,
                    "skew_usd": 0,
                })

            except Exception as e:
                logger.warning(f"BitgetCaller - Error fetching rate for {symbol}: {e}")
                continue

        return rates
