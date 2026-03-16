"""
RatesAPIClient — Fetches opportunity & rate data from the rates.lekker.design backend.

Endpoints consumed:
  GET /api/rates/opportunities?limit=50
      → list of opportunity dicts with:
        ticker, var_rate_annual, cex_exchange, cex_rate_annual,
        spread_annual, direction, daily_pnl_10k/50k/100k,
        var_mark_price, volume_24h

  GET /api/rates/summary
      → { total_markets_tracked, total_opportunities, best_spread_ticker,
          best_spread_annual, best_daily_10k, avg_spread_annual, updated_at }

  GET /api/rates/history?ticker={ticker}&hours=168
      → per-exchange historical rate timeseries

This client is intended as a *read-only* data feed for the arb bot.
It does NOT execute trades — that responsibility stays with the per-exchange
TxExecution modules.
"""

import os
import requests
from GlobalUtils.logger import logger
from GlobalUtils.globalUtils import normalize_funding_rate_to_8hrs

# Default base URL — override with RATES_API_BASE env var
DEFAULT_BASE_URL = "https://rates.lekker.design"


class RatesAPIClient:
    def __init__(self, base_url: str = None):
        self.base_url = (
            base_url
            or os.getenv("RATES_API_BASE")
            or DEFAULT_BASE_URL
        )
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    # ─── Public helpers ────────────────────────────────────────────

    def get_opportunities(self, limit: int = 50) -> list:
        """Fetch top opportunities from the rates API."""
        try:
            resp = self.session.get(
                f"{self.base_url}/api/rates/opportunities",
                params={"limit": limit},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return data
            # Some backends wrap in { "data": [...] }
            return data.get("data", data.get("opportunities", []))
        except Exception as e:
            logger.error(f"RatesAPIClient - Failed to fetch opportunities: {e}")
            return []

    def get_summary(self) -> dict:
        """Fetch the rates summary (market counts, best spread, etc.)."""
        try:
            resp = self.session.get(
                f"{self.base_url}/api/rates/summary",
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"RatesAPIClient - Failed to fetch summary: {e}")
            return {}

    def get_history(self, ticker: str, hours: int = 168) -> dict:
        """Fetch historical rate data for a ticker."""
        try:
            resp = self.session.get(
                f"{self.base_url}/api/rates/history",
                params={"ticker": ticker, "hours": hours},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"RatesAPIClient - Failed to fetch history for {ticker}: {e}")
            return {}

    # ─── Conversion to arb-bot format ──────────────────────────────

    def opportunities_to_funding_rates(self, opportunities: list = None) -> list:
        """
        Convert rates-API opportunity objects into the funding_rate dicts
        that the MatchingEngine expects:
            { symbol, exchange, funding_rate, skew_usd }

        Each opportunity from the API represents a *spread* between Variational
        and a CEX. We emit two rate entries per opportunity — one for the
        Variational leg and one for the CEX leg.

        Annual rates are converted to 8-hour rates for compatibility with
        the existing matching engine.
        """
        if opportunities is None:
            opportunities = self.get_opportunities()

        funding_rates = []
        for opp in opportunities:
            try:
                ticker = opp.get("ticker", "").upper()
                if not ticker:
                    continue

                var_rate_annual = float(opp.get("var_rate_annual", 0))
                cex_rate_annual = float(opp.get("cex_rate_annual", 0))
                cex_exchange = opp.get("cex_exchange", "Unknown")

                # Convert annual % → 8-hour fraction
                # annual_rate / 100 / (365.25 * 3) ≈ per-8h rate
                var_rate_8h = var_rate_annual / 100 / (365.25 * 3)
                cex_rate_8h = cex_rate_annual / 100 / (365.25 * 3)

                # Variational leg
                funding_rates.append({
                    "symbol": ticker,
                    "exchange": "Variational",
                    "funding_rate": var_rate_8h,
                    "skew_usd": 0,  # not available from API
                })

                # CEX leg
                funding_rates.append({
                    "symbol": ticker,
                    "exchange": cex_exchange,
                    "funding_rate": cex_rate_8h,
                    "skew_usd": 0,
                })

            except Exception as e:
                logger.warning(f"RatesAPIClient - Skipping opportunity {opp}: {e}")
                continue

        return funding_rates
