"""Order placement functions.

Every function here places a LIVE MARKET ORDER on a real brokerage
account and can move real money. There is no simulation mode and no
dry-run flag — the library deliberately stays small.

All trade functions:

1. Authenticate with the stored session token first
   (:func:`robinhood_agent.auth.ensure_login`).
2. Call a ``robin_stocks`` order function.
3. Normalize the API reply into ``{"order_id", "state", "raw"}``.

``robin_stocks`` reports API-level rejections by returning a dict that
contains an error message string instead of an order ``id``. Such replies
are converted into :class:`RuntimeError` so callers never treat a failed
order as a successful one.
"""

import robin_stocks.robinhood as r

from .auth import ensure_login

VALID_TIME_IN_FORCE = ("gfd", "gtc", "ioc", "fok", "opg")


def _normalize_order_result(result, context):
    """Validate and normalize a ``robin_stocks`` order response.

    Parameters
    ----------
    result : dict
        The raw response from an order function.
    context : str
        Short human-readable context for error messages
        (e.g. ``"buy by price 'AAPL'"``).

    Returns
    -------
    dict
        ``{"order_id": str or None, "state": str or None, "raw": result}``

    Raises
    ------
    RuntimeError
        If the reply is empty or carries an API error message instead of
        an accepted order.
    """
    if not result:
        raise RuntimeError(
            f"{context}: Robinhood returned an empty response; the order status is unknown."
        )

    error_message = result.get("message") or result.get("detail")
    has_order_id = "id" in result and result["id"] is not None

    if not has_order_id and error_message:
        raise RuntimeError(f"{context}: Robinhood rejected the order - {error_message}")
    if not has_order_id:
        raise RuntimeError(
            f"{context}: Robinhood returned a response without an order id. "
            f"Check order status in the app before retrying. Response: {result}"
        )

    return {
        "order_id": result["id"],
        "state": result.get("state"),
        "raw": result,
    }


def buy_by_price(symbol, amount, time_in_force="gfd"):
    """Buy ``amount`` US dollars of ``symbol`` as a fractional market order.

    Parameters
    ----------
    symbol : str
        Ticker symbol, e.g. ``"AAPL"``.
    amount : float
        Dollar amount to spend. Must be greater than zero.
    time_in_force : str, optional
        ``"gfd"`` (good for day) by default; ``"gtc"``, ``"ioc"``,
        ``"fok"``, and ``"opg"`` are also accepted.

    Returns
    -------
    dict
        ``{"order_id": ..., "state": ..., "raw": ...}``.

    Raises
    ------
    ValueError
        If ``amount`` is not greater than zero, or ``time_in_force`` is
        not recognized.
    RuntimeError
        If Robinhood rejects the order.
    """
    if not amount or float(amount) <= 0:
        raise ValueError(f"amount must be greater than zero (got {amount!r}).")
    if time_in_force not in VALID_TIME_IN_FORCE:
        raise ValueError(
            f"time_in_force must be one of {VALID_TIME_IN_FORCE}, got {time_in_force!r}."
        )

    ensure_login()
    result = r.order_buy_fractional_by_price(symbol, float(amount), timeInForce=time_in_force)
    return _normalize_order_result(result, f"buy by price '{symbol}' (${float(amount):.2f})")


def sell_by_price(symbol, amount, time_in_force="gfd"):
    """Sell ``amount`` US dollars of ``symbol`` as a fractional market order.

    Parameters
    ----------
    symbol : str
        Ticker symbol, e.g. ``"AAPL"``.
    amount : float
        Dollar amount to sell. Must be greater than zero.
    time_in_force : str, optional
        ``"gfd"`` (good for day) by default; other Robinhood-supported
        values are accepted.

    Returns
    -------
    dict
        ``{"order_id": ..., "state": ..., "raw": ...}``.

    Raises
    ------
    ValueError
        If ``amount`` is not greater than zero, or ``time_in_force`` is
        not recognized.
    RuntimeError
        If Robinhood rejects the order.
    """
    if not amount or float(amount) <= 0:
        raise ValueError(f"amount must be greater than zero (got {amount!r}).")
    if time_in_force not in VALID_TIME_IN_FORCE:
        raise ValueError(
            f"time_in_force must be one of {VALID_TIME_IN_FORCE}, got {time_in_force!r}."
        )

    ensure_login()
    result = r.order_sell_fractional_by_price(symbol, float(amount), timeInForce=time_in_force)
    return _normalize_order_result(result, f"sell by price '{symbol}' (${float(amount):.2f})")


def sell_by_quantity(symbol, quantity):
    """Sell ``quantity`` whole shares of ``symbol`` as a market order.

    Parameters
    ----------
    symbol : str
        Ticker symbol, e.g. ``"AAPL"``.
    quantity : int
        Number of shares to sell. Must be greater than zero.

    Returns
    -------
    dict
        ``{"order_id": ..., "state": ..., "raw": ...}``.

    Raises
    ------
    ValueError
        If ``quantity`` is not greater than zero.
    RuntimeError
        If Robinhood rejects the order.
    """
    if not quantity or int(quantity) <= 0:
        raise ValueError(f"quantity must be greater than zero (got {quantity!r}).")

    ensure_login()
    result = r.order_sell_market(symbol, int(quantity))
    return _normalize_order_result(result, f"sell by quantity '{symbol}' ({int(quantity)} shares)")


__all__ = ["buy_by_price", "sell_by_price", "sell_by_quantity", "VALID_TIME_IN_FORCE"]