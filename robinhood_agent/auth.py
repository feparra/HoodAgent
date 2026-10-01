"""Authentication helpers for the Robinhood Agent library.

All login flows delegate to ``robin_stocks``, which is responsible for
obtaining, refreshing, and storing session tokens. This module never
handles, stores, or logs credentials itself.

Session token storage
---------------------

``robin_stocks`` keeps the encrypted session token on disk (by default
in ``~/.tokens/robinhood.pickle``), expanded via :func:`pathlib.Path.home`.
The path is owned by the underlying library; this code only needs to
know it exists so users can delete the file to fully invalidate a session.

Security notes
--------------

* Never hardcode credentials in source, notebooks, or environment files
  committed to version control.
* Multi-factor authentication (MFA/SMS/Device) codes are handled by
  ``robin_stocks`` itself: when required, it prompts for the code on the
  terminal during :func:`login`. No MFA code ever passes through this
  module.
* If a token may have been exposed, remove the pickle file and call
  :func:`logout` to invalidate the session server-side.
"""

import getpass
from pathlib import Path

import robin_stocks.robinhood as r

# Documented (not used for I/O) so users can locate and, if needed, delete
# the token file robin_stocks created. The home directory is resolved at
# import time from the OS and is never hardcoded.
DEFAULT_TOKEN_PATH = Path.home() / ".tokens" / "robinhood.pickle"


def ensure_login() -> None:
    """Log in using the stored session token, or exit if that fails.

    Calls ``robin_stocks`` login with ``store_session=True`` and no
    credentials: the library reuses the stored token automatically when
    one is available.

    On failure the process exits with status 1 and a clear message telling
    the user to run ``python -m robinhood_agent login`` first. Designed for
    scripts and autonomous agents that run unattended.

    Raises
    ------
    SystemExit
        If authentication with the stored token fails (exit code 1).
    """
    try:
        r.login(store_session=True)
    except Exception as exc:  # noqa: BLE001 - surfaced verbatim to the user
        print("Authentication failed using the stored session token.")
        print(f"Details: {exc}")
        print("Run 'python -m robinhood_agent login' to sign in and store a new session.")
        raise SystemExit(1) from exc


def login() -> None:
    """Interactive login that stores a new session token.

    Prompts for the Robinhood email and password on the terminal (the
    password is read with ``getpass`` so it is not echoed) and hands them
    straight to ``robin_stocks`` with ``store_session=True``. If
    Robinhood requires it, ``robin_stocks`` will prompt for an MFA code
    on its own.
    """
    print("\nRobinhood Agent - interactive login")
    print("Credentials are not written to any file; they are passed directly to Robinhood.")
    print(f"The session token will be stored by robin_stocks at: {DEFAULT_TOKEN_PATH}\n")

    username = input("Robinhood email: ").strip()
    password = getpass.getpass("Password (hidden while typing): ")

    print("\nConnecting to Robinhood...")
    try:
        r.login(username=username, password=password, store_session=True)
        profile = r.build_user_profile()
        cash = profile.get("cash", "0.00")
        print("\nLogin successful.")
        print(f"Cash available: ${cash}")
        print("The session token is stored and will be used automatically for later calls.")
    except Exception as exc:  # noqa: BLE001 - surfaced verbatim to the user
        print(f"\nLogin failed: {exc}")
        raise SystemExit(1) from exc


def logout() -> None:
    """Log out and note that the stored session token is deleted.

    ``robin_stocks``' logout removes the pickled token file it created, so
    the session can no longer be resumed unattended. Call this whenever
    the machine is no longer trusted or before handing a laptop back.
    """
    r.logout()
    print("Logged out. The stored session token has been deleted.")


__all__ = ["ensure_login", "login", "logout", "DEFAULT_TOKEN_PATH"]