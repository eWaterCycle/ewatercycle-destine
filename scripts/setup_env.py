"""Create or repair the .env file holding the Earth Data Hub API key.

Run it from anywhere in the repository::

    python scripts/setup_env.py             # ask for the key if it is missing
    python scripts/setup_env.py --key ...   # non-interactive
    python scripts/setup_env.py --check     # also ask the Hub whether it works
    python scripts/setup_env.py --force     # replace a key that is already there

It leaves an existing, plausible-looking key alone, so it is safe to run
repeatedly. Any other variables in the file are preserved.

Note what this does *not* do: the library never reads ``.env``. It looks at the
``EDH_API_KEY`` environment variable and then at ``~/.netrc``, because reading
dotfiles out of the working directory is the caller's business, not a library's.
So the file this writes has to be loaded by whatever runs your code -- the
script prints the usual ways -- or you can skip it and put the key in
``~/.netrc`` instead, which needs no loading at all.
"""

import argparse
import base64
import os
import sys
import urllib.error
import urllib.request
from getpass import getpass
from pathlib import Path

from ewatercycle_destine.auth import (
    API_KEY_PAGE,
    API_KEY_VARIABLE,
    DEFAULT_LOGIN,
    EDH_HOST,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

PLACEHOLDERS = frozenset(
    {"", "changeme", "todo", "xxx", "your-api-key", "<your-api-key>", "none"}
)
"""Values that are present in the file but are not actually a key."""

# Any path answers 401 when the key is wrong, because Earth Data Hub checks
# credentials before it routes, so the probe does not depend on the slug.
PROBE_URL = (
    f"https://{EDH_HOST}/climate-dt-2/"
    "IFS-FESOM-hist-sfc-hourly-standard-v0.zarr/zarr.json"
)

REJECTED = (401, 403)


def read_key(path: Path) -> str | None:
    """Return the API key in a .env file, or None if there is not a usable one.

    Args:
        path: The .env file. It need not exist.

    Returns:
        The key, or None if the file is absent, has no ``EDH_API_KEY`` line, or
        that line holds an obvious placeholder.
    """
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            continue
        name, _, value = stripped.partition("=")
        if name.strip() != API_KEY_VARIABLE:
            continue
        key = value.strip().strip("'\"")
        return None if key.lower() in PLACEHOLDERS else key
    return None


def write_key(path: Path, key: str) -> None:
    """Write the API key into a .env file, keeping whatever else is in it.

    Args:
        path: The .env file. Created if absent.
        key: The API key to store.
    """
    line = f"{API_KEY_VARIABLE}={key}"

    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, existing in enumerate(lines):
            name, separator, _ = existing.strip().partition("=")
            if separator and name.strip() == API_KEY_VARIABLE:
                lines[index] = line
                break
        else:
            lines.append(line)
    else:
        lines = [
            "# DestinE Earth Data Hub credentials.",
            f"# Get a key from {API_KEY_PAGE}",
            line,
        ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    if os.name == "posix":
        path.chmod(0o600)


def key_works(key: str) -> bool | None:
    """Ask Earth Data Hub whether it accepts a key.

    Args:
        key: The API key to test.

    Returns:
        True if the Hub accepted it, False if it rejected it, None if the
        question could not be asked (no network, for instance).
    """
    token = base64.b64encode(f"{DEFAULT_LOGIN}:{key}".encode()).decode()
    request = urllib.request.Request(
        PROBE_URL, headers={"Authorization": f"Basic {token}"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            return response.status not in REJECTED
    except urllib.error.HTTPError as error:
        # Anything that is not a credentials error means the key got through,
        # even a 404 for a store slug that has since been renamed.
        return error.code not in REJECTED
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"  could not reach {EDH_HOST}: {error}")
        return None


def report(path: Path) -> None:
    """Explain what still has to happen for the file to have any effect."""
    print(f"\n{path} is ready. The library does not read it by itself, so either:")
    print("  - load it in your session, e.g.")
    print(f"      export $(grep -v '^#' {path.name} | xargs)      # bash/zsh")
    print("      from dotenv import load_dotenv; load_dotenv()  # python")
    print(f"  - or put the key in ~/.netrc under 'machine {EDH_HOST}', which")
    print("    ewatercycle_destine.auth reads without any loading step.")


def obtain_key(supplied: str | None) -> str | None:
    """Find a key to write: the one supplied, the environment's, or a prompt.

    Args:
        supplied: The key passed on the command line, if any.

    Returns:
        The key, or None if there was no way to obtain one.
    """
    key = supplied or os.environ.get(API_KEY_VARIABLE) or ""
    if key:
        source = "--key" if supplied else f"the {API_KEY_VARIABLE} environment variable"
        print(f"Taking the key from {source}.")
    elif sys.stdin.isatty():
        print(f"No key found. Get one from {API_KEY_PAGE}")
        key = getpass("Earth Data Hub API key (not echoed): ")
    else:
        print(
            f"No key available. Pass --key, or set {API_KEY_VARIABLE}, or run "
            f"this from a terminal so it can prompt. "
            f"Get a key from {API_KEY_PAGE}",
            file=sys.stderr,
        )
        return None

    key = key.strip()
    if key.lower() in PLACEHOLDERS:
        print("That is not a key.", file=sys.stderr)
        return None
    return key


def warn_if_committable() -> None:
    """Warn when .env is not ignored, so a key cannot be committed by accident."""
    gitignore = REPO_ROOT / ".gitignore"
    ignored = gitignore.is_file() and ".env" in gitignore.read_text(encoding="utf-8")
    if not ignored:
        print("WARNING: .env is not in .gitignore. Add it before committing.")


def check_existing(key: str, path: Path, verify: bool) -> int:
    """Report on a key that is already in the file. Returns an exit code.

    Args:
        key: The key found in the file.
        path: The file it was found in.
        verify: Whether to ask Earth Data Hub about it.

    Returns:
        0 unless the Hub rejected the key.
    """
    print(f"{path} already holds an {API_KEY_VARIABLE}.")
    if not verify:
        return 0
    accepted = key_works(key)
    if accepted is False:
        print("  Earth Data Hub rejected it.")
        print("  Re-run with --force to replace it.")
        return 1
    if accepted:
        print("  Earth Data Hub accepted it.")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Create or repair the .env file. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--key", help="the API key; prompted for when omitted")
    parser.add_argument(
        "--path",
        type=Path,
        default=REPO_ROOT / ".env",
        help="which .env file to write (default: the repository root)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="ask Earth Data Hub whether the key is accepted",
    )
    parser.add_argument(
        "--force", action="store_true", help="replace a key that is already there"
    )
    args = parser.parse_args(argv)

    existing = read_key(args.path)
    if existing is not None and not args.force:
        return check_existing(existing, args.path, args.check)

    key = args.key or os.environ.get(API_KEY_VARIABLE) or ""
    if key:
        source = "--key" if args.key else f"the {API_KEY_VARIABLE} environment variable"
        print(f"Taking the key from {source}.")
    elif sys.stdin.isatty():
        print(f"No key found. Get one from {API_KEY_PAGE}")
        key = getpass("Earth Data Hub API key (not echoed): ")
    else:
        print(
            f"No key available. Pass --key, or set {API_KEY_VARIABLE}, or run this "
            f"from a terminal so it can prompt.\nGet a key from {API_KEY_PAGE}",
            file=sys.stderr,
        )
        return 1

    key = key.strip()
    if key.lower() in PLACEHOLDERS:
        print("That is not a key.", file=sys.stderr)
        return 1

    if args.check:
        accepted = key_works(key)
        if accepted is False:
            print("Earth Data Hub rejected that key; nothing written.", file=sys.stderr)
            return 1
        if accepted:
            print("Earth Data Hub accepted it.")

    write_key(args.path, key)
    print(f"Wrote {API_KEY_VARIABLE} to {args.path}.")

    warn_if_committable()
    report(args.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
