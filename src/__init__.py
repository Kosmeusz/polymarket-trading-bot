"""
Trading Demo - Modular Polymarket Trading Bot

A production-ready trading bot with:
- Encrypted private key storage
- Gasless transactions via Builder Program
- Modular architecture for easy extension
- Comprehensive testing

Example usage:
    from src.bot import TradingBot
    bot = TradingBot()
    await bot.place_order(token_id, price, size, "BUY")
"""

from .bot import TradingBot
from .signer import OrderSigner
from .client import ApiClient, ClobClient, RelayerClient
from .crypto import KeyManager
from .config import Config

__version__ = "1.0.0"
__all__ = [
    "TradingBot",
    "OrderSigner",
    "ApiClient",
    "ClobClient",
    "RelayerClient",
    "KeyManager",
    "Config",
]
