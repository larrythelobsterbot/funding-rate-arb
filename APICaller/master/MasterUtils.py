from GlobalUtils.logger import logger

TARGET_TOKENS = [
    {"token": "BTC", "is_target": True},
    {"token": "ETH", "is_target": True},
    {"token": "SOL", "is_target": False},
    {"token": "ARB", "is_target": False},
    {"token": "BNB", "is_target": False},
    {"token": "DOGE", "is_target": False},
    {"token": "AVAX", "is_target": False},
    {"token": "NEAR", "is_target": False},
    {"token": "AAVE", "is_target": False},
    {"token": "LINK", "is_target": False},
    {"token": "UNI", "is_target": False},
    {"token": "OP", "is_target": False},
    {"token": "PEPE", "is_target": False},
]

# ─── Exchange roster ───────────────────────────────────────────────
# Keep from template:  Binance, ByBit, OKX, GMX
# Removed:             Synthetix, Perennial, HMX
# New (Phase 2+):      Variational, Hyperliquid, EdgeX, Lighter, Gate.io, Bitget
TARGET_EXCHANGES = [
    {"exchange": "Binance", "is_target": True},
    {"exchange": "ByBit", "is_target": True},
    {"exchange": "OKX", "is_target": False},
    {"exchange": "GMX", "is_target": True},
    # Phase 2 — uncomment as modules are built
    # {"exchange": "Variational", "is_target": False},
    # {"exchange": "Hyperliquid", "is_target": False},
    # {"exchange": "EdgeX", "is_target": False},
    # {"exchange": "Lighter", "is_target": False},
    # {"exchange": "GateIO", "is_target": False},
    # {"exchange": "Bitget", "is_target": False},
]


def get_target_exchanges() -> list:
    try:
        exchanges = [exchange["exchange"] for exchange in TARGET_EXCHANGES if exchange["is_target"]]
        return exchanges
    except Exception as e:
        logger.error(f"MasterAPICallerUtils - Error retrieving target exchanges: {e}")
        return []


def get_all_target_token_lists() -> dict:
    """Returns a dict keyed by exchange name → list of formatted token symbols."""
    try:
        return {
            "Binance": get_target_tokens_for_binance(),
            "ByBit": get_target_tokens_for_bybit(),
            "OKX": get_target_tokens_for_OKX(),
            "GMX": get_target_tokens_for_GMX(),
            # New exchanges — use raw symbol list (no suffix needed)
            "Variational": get_target_tokens_raw(),
            "Hyperliquid": get_target_tokens_raw(),
            "EdgeX": get_target_tokens_raw(),
            "Lighter": get_target_tokens_raw(),
            "GateIO": get_target_tokens_raw(),
            "Bitget": get_target_tokens_raw(),
        }
    except Exception as e:
        logger.error(f"MasterAPICallerUtils - Error retrieving all target token lists: {e}")
        return {}


def get_target_tokens_for_binance() -> list:
    try:
        symbols = [token["token"] + "USDT" for token in TARGET_TOKENS if token["is_target"]]
        return symbols
    except Exception as e:
        logger.error(f"MasterAPICallerUtils - Error retrieving target tokens for Binance: {e}")
        return []


def get_target_tokens_for_OKX() -> list:
    try:
        symbols = [token["token"] + "-USDT-SWAP" for token in TARGET_TOKENS if token["is_target"]]
        return symbols
    except Exception as e:
        logger.error(f"MasterAPICallerUtils - Error retrieving target tokens for OKX: {e}")
        return []


def get_target_tokens_for_bybit() -> list:
    try:
        symbols = [token["token"] + "USDT" for token in TARGET_TOKENS if token["is_target"]]
        return symbols
    except Exception as e:
        logger.error(f"MasterAPICallerUtils - Error retrieving target tokens for ByBit: {e}")
        return []


def get_target_tokens_for_GMX() -> list:
    try:
        symbols = [token["token"] for token in TARGET_TOKENS if token["is_target"]]
        return symbols
    except Exception as e:
        logger.error(f"MasterAPICallerUtils - Error retrieving target tokens for GMX: {e}")
        return []


def get_target_tokens_raw() -> list:
    """Raw symbol list (BTC, ETH, ...) — used by new exchanges that handle
    their own symbol formatting internally."""
    try:
        symbols = [token["token"] for token in TARGET_TOKENS if token["is_target"]]
        return symbols
    except Exception as e:
        logger.error(f"MasterAPICallerUtils - Error retrieving raw target tokens: {e}")
        return []
