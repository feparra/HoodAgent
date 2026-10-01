"""Robinhood Agent.

A thin, safe wrapper over the ``robin_stocks`` library that lets any AI
agent or script connect to Robinhood, read portfolio data, and place
market orders (fractional by price, or whole shares).

Design goals:

* Minimal surface area — a handful of well-named functions.
* Agent-friendly — plain ``dict``/``list`` returns, no custom classes.
* Safe defaults — a stored-session login guard runs before every trade.

Robinhood does not publish an official public trading API; this module is
built on the unofficial ``robin_stocks`` library and therefore carries the
same risks as any unofficial integration. Trading involves risk.
"""

from .auth import ensure_login, login, logout
from .portfolio import (
    get_account_profile,
    get_cash,
    get_positions,
    get_quote,
    get_top_100,
)
from .trading import buy_by_price, sell_by_price, sell_by_quantity

__all__ = [
    "ensure_login",
    "login",
    "logout",
    "get_cash",
    "get_account_profile",
    "get_positions",
    "get_quote",
    "get_top_100",
    "buy_by_price",
    "sell_by_price",
    "sell_by_quantity",
]

__version__ = "0.1.0"