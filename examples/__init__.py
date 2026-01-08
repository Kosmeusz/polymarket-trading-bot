"""
Example Trading Strategies

This package contains example trading strategies and usage examples
for the Polymarket Trading Bot.

Examples:
    from examples.basic_trading import run_example

    run_example()
"""

from .basic_trading import main as run_basic_example
from .strategy_example import (
    BaseStrategy,
    MeanReversionStrategy,
    GridTradingStrategy,
    run_example_strategy
)

__all__ = [
    "run_basic_example",
    "BaseStrategy",
    "MeanReversionStrategy",
    "GridTradingStrategy",
    "run_example_strategy",
]
