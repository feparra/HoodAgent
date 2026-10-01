"""Example: programmatic use of the Robinhood Agent library.

This shows how an AI agent (or any script) would drive the library from
Python instead of the CLI.

WARNING: This example places LIVE MARKET ORDERS on a real brokerage
account. Any call to buy_by_price/sell_by_price/sell_by_quantity spends
or moves REAL MONEY with no simulation or dry-run mode. Read the code
before running it; start with the smallest possible dollar amount.
"""

from robinhood_agent import (
    buy_by_price,
    ensure_login,
    get_cash,
    get_quote,
)

DOLLAR_LIMIT = 1.00  # Hard safety cap for this example. Keep it tiny.


def main():
    # 1. Authenticate using the stored session token. If no token exists,
    #    this exits with status 1 and tells the user how to log in.
    ensure_login()

    # 2. Check available cash before sizing any order.
    cash = get_cash()
    print(f"Available cash: {cash}")
    if cash is None or float(cash) < DOLLAR_LIMIT:
        print("Not enough cash for the minimum example order; aborting.")
        return

    # 3. Look up the latest quote for the symbol we are interested in.
    price = get_quote("AAPL")
    print(f"Latest AAPL price: {price}")

    # 4. Place a small fractional buy by dollar amount (live order!).
    order = buy_by_price("AAPL", DOLLAR_LIMIT)
    print(f"Order id: {order['order_id']}")
    print(f"State:    {order['state']}")

    # 5. Inspect the full API reply if more detail is needed.
    #    order['raw'] is the unmodified robin_stocks response.
    print(f"Raw response keys: {sorted(order['raw'].keys())}")


if __name__ == "__main__":
    main()