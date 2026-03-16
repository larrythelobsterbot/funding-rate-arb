from APICaller.Binance.binanceCaller import BinanceCaller
from APICaller.ByBit.ByBitCaller import ByBitCaller
from APICaller.GMX.GMXCaller import GMXCaller
from APICaller.master.MasterUtils import get_all_target_token_lists, get_target_exchanges
from GlobalUtils.logger import *
import json


# ─── Lazy exchange loader ──────────────────────────────────────────
# Only import and instantiate exchanges that are set as targets.
# This avoids import-time crashes for exchanges whose env vars
# aren't configured (e.g. OKX API keys missing).

def _make_exchange(name: str):
    """Factory: import and instantiate a caller by exchange name."""
    if name == "Binance":
        return BinanceCaller()
    elif name == "ByBit":
        return ByBitCaller()
    elif name == "GMX":
        return GMXCaller()
    elif name == "OKX":
        from APICaller.Okx.okxCaller import OKXCaller
        return OKXCaller()
    elif name == "Variational":
        from APICaller.Variational.VariationalCaller import VariationalCaller
        return VariationalCaller()
    elif name == "Hyperliquid":
        from APICaller.Hyperliquid.HyperliquidCaller import HyperliquidCaller
        return HyperliquidCaller()
    elif name == "EdgeX":
        from APICaller.EdgeX.EdgeXCaller import EdgeXCaller
        return EdgeXCaller()
    elif name == "Lighter":
        from APICaller.Lighter.LighterCaller import LighterCaller
        return LighterCaller()
    elif name == "GateIO":
        from APICaller.GateIO.GateIOCaller import GateIOCaller
        return GateIOCaller()
    elif name == "Bitget":
        from APICaller.Bitget.BitgetCaller import BitgetCaller
        return BitgetCaller()
    else:
        logger.warning(f"MasterAPICaller - No caller implemented for exchange: {name}")
        return None


class MasterCaller:
    def __init__(self):
        self.target_exchanges = get_target_exchanges()
        self.token_lists = get_all_target_token_lists()

        # Only instantiate callers for targeted exchanges
        self.exchange_objects = {}
        for name in self.target_exchanges:
            try:
                caller = _make_exchange(name)
                if caller:
                    self.exchange_objects[name] = caller
            except Exception as e:
                logger.error(f"MasterAPICaller - Failed to instantiate {name}: {e}")

    def get_funding_rates(self) -> list:
        funding_rates = []
        if not self.exchange_objects:
            logger.error("MasterAPICaller - No exchanges available for fetching funding rates.")
            return funding_rates

        for exchange_name, exchange in self.exchange_objects.items():
            tokens = self.token_lists.get(exchange_name, [])
            if not tokens:
                logger.warning(f"MasterAPICaller - No tokens available for {exchange_name}. Skipping.")
                continue

            try:
                rates = exchange.get_funding_rates(tokens)
                if rates:
                    funding_rates.extend(rates)
                else:
                    logger.warning(f"MasterAPICaller - No funding rates returned from {exchange_name}.")
            except Exception as e:
                logger.error(f"MasterAPICaller - Error getting funding rates from {exchange_name}: {e}")

        if not funding_rates:
            logger.error("MasterAPICaller - No funding rates obtained from any exchanges.")
            return None

        return funding_rates
