"""Read-only portfolio and market data helpers.

These functions only read data from Robinhood via ``robin_stocks``. They
never place orders. Callers (interactive users or autonomous agents) are
expected to have a working session first — call
:func:`robinhood_agent.auth.ensure_login` before using them.
"""

import robin_stocks.robinhood as r


def get_cash():
    """Return the available cash balance as a value (or ``None``).

    Returns
    -------
    float or str or None
        The ``cash`` field of the user profile. ``None`` when the field
        is absent (for example when authentication failed).
    """
    profile = r.build_user_profile()
    return profile.get("cash")


def get_account_profile():
    """Return the account profile with buying power and cash extracted.

    Returns
    -------
    dict
        The full account profile as returned by ``robin_stocks``.
        ``buying_power`` and ``portfolio_cash`` are present as
        (possibly ``None``) keys through the raw payload itself; callers
        that only need one number may prefer :func:`get_cash`.

    Raises
    ------
    RuntimeError
        If Robinhood returns no account profile.
    """
    profile = r.load_account_profile()
    if not profile:
        raise RuntimeError("Robinhood did not return an account profile.")
    return {
        "buying_power": profile.get("buying_power"),
        "portfolio_cash": profile.get("portfolio_cash"),
        "raw": profile,
    }


def get_positions():
    """Return open stock positions as a list of plain dicts.

    Each position's instrument URL is resolved to its ticker symbol using
    ``robin_stocks``' symbol lookup.

    Returns
    -------
    list[dict]
        One dict per open position with the keys ``symbol``,
        ``quantity``, and ``average_buy_price``. Zero-quantity positions
        are filtered out.
    """
    positions = []
    for pos in r.get_open_stock_positions() or []:
        quantity = float(pos.get("quantity") or 0)
        if quantity == 0:
            continue
        positions.append(
            {
                "symbol": r.get_symbol_by_url(pos["instrument"]),
                "quantity": quantity,
                "average_buy_price": float(pos.get("average_buy_price") or 0),
            }
        )
    return positions


def get_quote(symbol):
    """Return the latest quote price for ``symbol``.

    ``robin_stocks``' price helper returns a list, so the first element is
    returned here.

    Parameters
    ----------
    symbol : str
        Ticker symbol, e.g. ``"AAPL"``.

    Returns
    -------
    str or float or None
        The most recent price for the symbol (a string in most cases);
        ``None`` when Robinhood has no quote for it.

    Raises
    ------
    RuntimeError
        When Robinhood returns an empty price list.
    """
    prices = r.get_latest_price(symbol)
    if not prices:
        raise RuntimeError(f"No price data returned for symbol '{symbol}'.")
    return prices[0]


def get_top_100():
    """Return Robinhood's top 100 most-popular instruments, unchanged.

    Returns
    -------
    list[dict]
        The raw payload from ``robin_stocks.get_top_100()``. Each item
        contains instrument metadata including a ``symbol`` key.
    """
    return r.get_top_100()


__all__ = [
    "get_cash",
    "get_account_profile",
    "get_positions",
    "get_quote",
    "get_top_100",
]