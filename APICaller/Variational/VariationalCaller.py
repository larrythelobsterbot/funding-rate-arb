"""
VariationalCaller — Fetch funding rates from the Variational protocol.

Phase 2 implementation options:
  1. Direct SDK: pip install variational-sdk (Python SDK)
  2. Via RatesAPI: the rates.lekker.design backend already tracks Variational rates
  3. REST/WebSocket: connect to Variational's Omni LP RFQ endpoints

For now, this stub uses the RatesAPI as a proxy, since it already
aggregates Variational data with zero additional infra.
"""

from GlobalUtils.logger import logger
from APICaller.RatesAPI.RatesAPIClient import RatesAPIClient


class VariationalCaller:
    def __init__(self):
        self.rates_client = RatesAPIClient()

    def get_funding_rates(self, symbols: list) -> list:
        """
        Fetch Variational funding rates for the given symbols.

        Returns list of dicts matching the arb-bot format:
            { symbol, exchange, funding_rate, skew_usd }
        """
        try:
            all_rates = self.rates_client.opportunities_to_funding_rates()
            # Filter to only Variational entries for our target symbols
            variational_rates = [
                r for r in all_rates
                if r["exchange"] == "Variational"
                and r["symbol"] in [s.upper().replace("USDT", "").replace("-SWAP", "") for s in symbols]
            ]
            return variational_rates

        except Exception as e:
            logger.error(f"VariationalCaller - Error fetching funding rates: {e}")
            return []
