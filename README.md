# Robinhood Agent

A minimal, agent-friendly Python module for Robinhood: log in, read your
portfolio, and place market orders (fractional by price, or whole shares).
Built as a thin wrapper over the [`robin_stocks`](https://github.com/jxmorris12/robin_stocks)
library so any AI agent or script can plug into it with a handful of plain
function calls.

## Security

* **Session token location.** `robin_stocks` stores the encrypted session
  token on disk at `~/.tokens/robinhood.pickle` (your home directory,
  never a project directory). This library never reads or writes that file.
* **No credentials in code.** Credentials are only ever entered interactively
  and passed straight to `robin_stocks`. Never hardcode them in source,
  notebooks, or committed environment files.
* **Repository protections.** The included `.gitignore` excludes `.env`,
  `.tokens/`, and `*.pickle` so tokens and secrets cannot be committed
  accidentally.
* **If a token is ever exposed**, log out (deletes the stored token) and
  additionally delete `~/.tokens/robinhood.pickle` manually to fully
  invalidate the session. Consider changing your Robinhood password.
* **Unofficial API.** Robinhood does not offer an official public trading
  API; `robin_stocks` is an unofficial library that talks to Robinhood's
  private endpoints. It may break without notice and use of it (and of this
  wrapper) is at your own responsibility with your own account.
* **Risk disclaimer.** Trading involves risk of loss. This project is
  software, not financial advice.

## Install

```bash
git clone <repository-url>
cd robinhood-agent
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Quickstart (CLI)

```bash
# One-time interactive login (stores a session token)
python -m robinhood_agent login

# Check buying power and cash
python -m robinhood_agent status

# List open positions
python -m robinhood_agent positions

# Get a quote
python -m robinhood_agent quote AAPL

# Buy $5.00 of AAPL (fractional market order, good for day)
python -m robinhood_agent buy AAPL 5.00

# Sell $5.00 of AAPL, or 1 whole share instead
python -m robinhood_agent sell AAPL 5.00
python -m robinhood_agent sell AAPL --shares 1

# Log out (deletes the stored session token)
python -m robinhood_agent logout
```

`buy` and `sell` place LIVE ORDERS that spend real money.

## Quickstart (library)

```python
from robinhood_agent import ensure_login, get_cash, get_quote, buy_by_price

ensure_login()
print(get_cash())            # available cash
print(get_quote("AAPL"))     # latest price
order = buy_by_price("AAPL", 1.00)   # live order!
print(order["order_id"], order["state"])
```

A complete commented walkthrough is in `examples/agent_usage.py`.

## API reference

| Function | Signature | Description |
| --- | --- | --- |
| `ensure_login` | `ensure_login() -> None` | Login via the stored session token; exits (status 1) telling the user to run `python -m robinhood_agent login` when it fails. |
| `login` | `login() -> None` | Interactive email/password login; stores a new session token and prints the cash balance. |
| `logout` | `logout() -> None` | Log out; deletes the stored session token. |
| `get_cash` | `get_cash()` | Available cash from the user profile. |
| `get_account_profile` | `get_account_profile() -> dict` | Account profile with `buying_power`, `portfolio_cash`, and the raw payload. |
| `get_positions` | `get_positions() -> list[dict]` | Open stock positions as `{symbol, quantity, average_buy_price}`. |
| `get_quote` | `get_quote(symbol)` | Latest price for a symbol (first element of the underlying list). |
| `get_top_100` | `get_top_100() -> list[dict]` | Robinhood's top 100 most-popular instruments (passthrough). |
| `buy_by_price` | `buy_by_price(symbol, amount, time_in_force="gfd") -> dict` | Buy `amount` dollars as a fractional market order. |
| `sell_by_price` | `sell_by_price(symbol, amount, time_in_force="gfd") -> dict` | Sell `amount` dollars as a fractional market order. |
| `sell_by_quantity` | `sell_by_quantity(symbol, quantity) -> dict` | Sell `quantity` whole shares as a market order. |

Trade functions return a normalized dict:

```python
{"order_id": "...", "state": "confirmed", "raw": {...}}
```

Robinhood rejections surface as `RuntimeError` with the API message, so a
failed order is never mistaken for a successful one.

## Scope

This library is intentionally **minimal**. It supports only:

* Market orders, either fractional by dollar amount or by whole share count.

It deliberately does **not** (yet) support:

* Limit or stop-loss orders
* Option contracts
* Crypto orders
* Order cancellation or modification
* Transfers, dividends, or tax documents

Treat these as future work.