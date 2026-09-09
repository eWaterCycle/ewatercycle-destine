"""Tests for scripts/setup_env.py.

The script is not part of the package, so it is loaded by path.
"""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "setup_env.py"
_spec = importlib.util.spec_from_file_location("setup_env", SCRIPT)
setup_env = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup_env)


def test_read_key_of_a_missing_file(tmp_path):
    assert setup_env.read_key(tmp_path / ".env") is None


def test_read_key(tmp_path):
    env = tmp_path / ".env"
    env.write_text("# a comment\nOTHER=something\nEDH_API_KEY=secret\n")

    assert setup_env.read_key(env) == "secret"


def test_read_key_strips_quotes(tmp_path):
    env = tmp_path / ".env"
    env.write_text('EDH_API_KEY="secret"\n')

    assert setup_env.read_key(env) == "secret"


@pytest.mark.parametrize("value", ["", "changeme", "<your-api-key>", "YOUR-API-KEY"])
def test_read_key_treats_placeholders_as_absent(tmp_path, value):
    env = tmp_path / ".env"
    env.write_text(f"EDH_API_KEY={value}\n")

    assert setup_env.read_key(env) is None


def test_write_key_creates_the_file(tmp_path):
    env = tmp_path / ".env"

    setup_env.write_key(env, "secret")

    assert setup_env.read_key(env) == "secret"
    assert "platform.destine.eu" in env.read_text()  # points at where to get one


def test_write_key_keeps_everything_else(tmp_path):
    env = tmp_path / ".env"
    env.write_text("OTHER=keepme\nEDH_API_KEY=old\n# trailing comment\n")

    setup_env.write_key(env, "new")

    assert env.read_text() == "OTHER=keepme\nEDH_API_KEY=new\n# trailing comment\n"


def test_write_key_appends_when_the_variable_is_absent(tmp_path):
    env = tmp_path / ".env"
    env.write_text("OTHER=keepme\n")

    setup_env.write_key(env, "secret")

    assert setup_env.read_key(env) == "secret"
    assert "OTHER=keepme" in env.read_text()


def test_obtain_key_prefers_the_argument(monkeypatch):
    monkeypatch.setenv("EDH_API_KEY", "from-environment")

    assert setup_env.obtain_key("from-argument") == "from-argument"


def test_obtain_key_falls_back_to_the_environment(monkeypatch):
    monkeypatch.setenv("EDH_API_KEY", "from-environment")

    assert setup_env.obtain_key(None) == "from-environment"


def test_obtain_key_rejects_a_placeholder():
    assert setup_env.obtain_key("changeme") is None


def test_obtain_key_gives_up_when_it_cannot_ask(monkeypatch):
    """Without a terminal there is nobody to prompt, so it must not block."""
    monkeypatch.delenv("EDH_API_KEY", raising=False)
    monkeypatch.setattr(setup_env.sys.stdin, "isatty", lambda: False)

    assert setup_env.obtain_key(None) is None


def test_main_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.delenv("EDH_API_KEY", raising=False)
    env = tmp_path / ".env"

    assert setup_env.main(["--key", "secret", "--path", str(env)]) == 0
    assert setup_env.main(["--key", "another", "--path", str(env)]) == 0
    assert setup_env.read_key(env) == "secret"


def test_main_replaces_with_force(tmp_path, monkeypatch):
    monkeypatch.delenv("EDH_API_KEY", raising=False)
    env = tmp_path / ".env"

    setup_env.main(["--key", "secret", "--path", str(env)])
    setup_env.main(["--key", "another", "--force", "--path", str(env)])

    assert setup_env.read_key(env) == "another"
