"""Authentication for the DestinE Earth Data Hub.

Earth Data Hub (``api.earthdatahub.destine.eu``) authenticates with a per-user
API key, which is HTTP basic auth: the key is the password, ``edh`` the login.
The key is issued on the DestinE platform under *Quota & API Keys*.

The key is looked up in two places, in order:

1. the ``EDH_API_KEY`` environment variable;
2. a ``~/.netrc`` (or ``~/_netrc`` on Windows) entry::

    machine api.earthdatahub.destine.eu
        login edh
        password <your-api-key>

Reading a ``.env`` file is deliberately not supported here: that is the
caller's concern, not a library's.
"""

import netrc
import os
from pathlib import Path
from typing import Any

import aiohttp

EDH_HOST = "api.earthdatahub.destine.eu"
API_KEY_VARIABLE = "EDH_API_KEY"
DEFAULT_LOGIN = "edh"
API_KEY_PAGE = "https://platform.destine.eu/ (Menu > Quota & API Keys)"


class MissingApiKeyError(RuntimeError):
    """Raised when no Earth Data Hub API key could be found."""


def _netrc_credentials(host: str) -> tuple[str, str] | None:
    """Return (login, key) from the user's netrc file, or None if absent."""
    for candidate in (Path.home() / ".netrc", Path.home() / "_netrc"):
        if not candidate.is_file():
            continue
        authenticators = netrc.netrc(str(candidate)).authenticators(host)
        if authenticators is None:
            continue
        login, _account, password = authenticators
        if password:
            return login or DEFAULT_LOGIN, password
    return None


def get_credentials(host: str = EDH_HOST) -> tuple[str, str]:
    """Return the basic-auth credentials for Earth Data Hub.

    Args:
        host: Host to look up in the netrc file.

    Returns:
        A (login, api_key) tuple.

    Raises:
        MissingApiKeyError: If neither the environment variable nor the netrc
            file provides a key.
    """
    api_key = os.environ.get(API_KEY_VARIABLE)
    if api_key:
        return DEFAULT_LOGIN, api_key

    credentials = _netrc_credentials(host)
    if credentials is not None:
        return credentials

    msg = (
        f"No Earth Data Hub API key found. Get one from {API_KEY_PAGE} and either "
        f"set the {API_KEY_VARIABLE} environment variable, or add to your "
        f"~/.netrc file:\n"
        f"    machine {host}\n"
        f"        login {DEFAULT_LOGIN}\n"
        f"        password <your-api-key>"
    )
    raise MissingApiKeyError(msg)


def storage_options(host: str = EDH_HOST) -> dict[str, Any]:
    """Return fsspec storage options that authenticate against Earth Data Hub.

    Args:
        host: Host to look up in the netrc file.

    Returns:
        A dict to pass as ``storage_options`` to :py:func:`xarray.open_dataset`.
    """
    login, api_key = get_credentials(host)
    return {
        "client_kwargs": {
            "auth": aiohttp.BasicAuth(login, api_key),
            "trust_env": True,
        }
    }
