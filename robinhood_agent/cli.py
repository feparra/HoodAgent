"""Command-line interface for the Robinhood Agent library.

Subcommands
-----------

login               Interactive login that stores a session token.
status              Print available cash and buying power.
positions           Print open stock positions.
quote SYMBOL        Print the latest price for SYMBOL.
buy SYMBOL AMOUNT   Buy AMOUNT dollars of SYMBOL (fractional market order).
sell SYMBOL AMOUNT  Sell AMOUNT dollars of SYMBOL.
sell SYMBOL --shares QTY
                    Sell QTY whole shares of SYMBOL (market order).

``buy`` and ``sell`` place live orders that spend or move real money.
"""

import argparse
import sys

import robin_stocks.robinhood as r

from .auth import ensure_login, login as interactive_login, logout as do_logout
from .portfolio import get_cash, get_positions, get_quote
from .trading import buy_by_price, sell_by_price, sell_by_quantity

PROG = "robinhood_agent"


def _fmt_price(value):
    """Format a numeric (or numeric-string) value as USD, best effort."""
    if value is None:
        return "n/a"
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def cmd_login(_args):
    """Handle the ``login`` subcommand."""
    interactive_login()


def cmd_logout(_args):
    """Handle the ``logout`` subcommand."""
    do_logout()


def cmd_status(_args):
    """Handle the ``status`` subcommand: cash and buying power."""
    ensure_login()
    cash = get_cash()
    profile = r.load_account_profile()
    buying_power = profile.get("buying_power") if profile else None
    print(f"Cash:            {_fmt_price(cash)}")
    print(f"Buying power:    {_fmt_price(buying_power)}")


def cmd_positions(_args):
    """Handle the ``positions`` subcommand."""
    ensure_login()
    positions = get_positions()
    if not positions:
        print("No open stock positions.")
        return
    print(f"{'Symbol':<8} {'Quantity':>12} {'Avg buy price':>16}")
    for pos in positions:
        print(
            f"{pos['symbol']:<8} {pos['quantity']:>12.8f} "
            f"{_fmt_price(pos['average_buy_price']):>16}"
        )


def cmd_quote(args):
    """Handle the ``quote`` subcommand."""
    ensure_login()
    print(f"{args.symbol.upper()}: {_fmt_price(get_quote(args.symbol))}")


def cmd_buy(args):
    """Handle the ``buy`` subcommand (live market order)."""
    ensure_login()
    result = buy_by_price(args.symbol, args.amount)
    print(f"Buy order sent for {args.symbol.upper()} ({_fmt_price(args.amount)}).")
    print(f"Order id: {result['order_id']}")
    print(f"State:    {result['state']}")


def cmd_sell(args):
    """Handle the ``sell`` subcommand (live market order)."""
    ensure_login()
    if args.shares is not None:
        result = sell_by_quantity(args.symbol, args.shares)
        detail = f"{args.shares} share(s)"
    else:
        result = sell_by_price(args.symbol, args.amount)
        detail = _fmt_price(args.amount)
    print(f"Sell order sent for {args.symbol.upper()} ({detail}).")
    print(f"Order id: {result['order_id']}")
    print(f"State:    {result['state']}")


def build_parser():
    """Build the argument parser for all subcommands."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Minimal agent-friendly Robinhood client: read portfolio data "
            "and place market orders. Live orders move real money."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("login", help="Interactive login; stores the session token.")
    subparsers.add_parser("logout", help="Log out and delete the stored session token.")

    p_status = subparsers.add_parser("status", help="Show available cash and buying power.")
    p_status.set_defaults(func=cmd_status)

    p_positions = subparsers.add_parser("positions", help="List open stock positions.")
    p_positions.set_defaults(func=cmd_positions)

    p_quote = subparsers.add_parser("quote", help="Show the latest price for a symbol.")
    p_quote.add_argument("symbol", help="Ticker symbol, e.g. AAPL")
    p_quote.set_defaults(func=cmd_quote)

    p_buy = subparsers.add_parser("buy", help="Buy by dollar amount (fractional market order).")
    p_buy.add_argument("symbol", help="Ticker symbol, e.g. AAPL")
    p_buy.add_argument("amount", type=float, help="Dollar amount to buy (must be > 0)")
    p_buy.set_defaults(func=cmd_buy)

    p_sell = subparsers.add_parser(
        "sell",
        help="Sell by dollar amount, or by share count with --shares.",
    )
    p_sell.add_argument("symbol", help="Ticker symbol, e.g. AAPL")
    p_sell.add_argument(
        "amount",
        type=float,
        nargs="?",
        default=None,
        help="Dollar amount to sell (used when --shares is not given)",
    )
    p_sell.add_argument(
        "--shares",
        type=int,
        default=None,
        help="Number of whole shares to sell instead of a dollar amount",
    )
    p_sell.set_defaults(func=cmd_sell)

    return parser


def main(argv=None):
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "func", None):
        parser.print_help()
        return 0

    try:
        args.func(args)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())