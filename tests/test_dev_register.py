from unittest.mock import patch

import pytest

from scripts.dev_register import (
    Identity,
    choose_identity,
    configure_git_identity,
    default_choice,
    parse_gh_accounts,
)


def test_choose_identity_uses_non_interactive_default() -> None:
    identities: list[Identity] = [
        {
            "source": "Local Git Config",
            "name": "Alice",
            "email": "alice@example.com",
            "login": "",
            "active": False,
        }
    ]

    with patch("sys.stdin.isatty", return_value=False):
        assert choose_identity(identities, None) == identities[0]


def test_choose_identity_uses_explicit_choice() -> None:
    identities: list[Identity] = [
        {
            "source": "one",
            "name": "One",
            "email": "one@example.com",
            "login": "one",
            "active": False,
        },
        {
            "source": "two",
            "name": "Two",
            "email": "two@example.com",
            "login": "two",
            "active": False,
        },
    ]

    assert choose_identity(identities, 2) == identities[1]


def test_choose_identity_rejects_zero() -> None:
    identities: list[Identity] = [
        {
            "source": "one",
            "name": "One",
            "email": "one@example.com",
            "login": "one",
            "active": False,
        }
    ]

    with pytest.raises(SystemExit):
        choose_identity(identities, 0)


def test_parse_gh_accounts_marks_active_account_first() -> None:
    status_output = """
github.com
  ✓ Logged in to github.com account theontho (keyring)
  - Active account: true

  ✓ Logged in to github.com account warkingtime (keyring)
  - Active account: false
"""

    assert parse_gh_accounts(status_output) == [("theontho", True), ("warkingtime", False)]


def test_default_choice_prefers_active_github_account() -> None:
    identities: list[Identity] = [
        {
            "source": "Local Git Config",
            "name": "Local",
            "email": "local@example.com",
            "login": "",
            "active": False,
        },
        {
            "source": "GitHub (active account: theontho)",
            "name": "theontho",
            "email": "theontho@users.noreply.github.com",
            "login": "theontho",
            "active": True,
        },
    ]

    assert default_choice(identities) == 2


def test_choose_identity_non_interactive_prefers_active_account() -> None:
    identities: list[Identity] = [
        {
            "source": "GitHub (account: warkingtime)",
            "name": "warkingtime",
            "email": "warkingtime@users.noreply.github.com",
            "login": "warkingtime",
            "active": False,
        },
        {
            "source": "GitHub (active account: theontho)",
            "name": "theontho",
            "email": "theontho@users.noreply.github.com",
            "login": "theontho",
            "active": True,
        },
    ]

    with patch("sys.stdin.isatty", return_value=False):
        assert choose_identity(identities, None) == identities[1]


def test_configure_git_identity_updates_local_git_config() -> None:
    identity: Identity = {
        "source": "GitHub (active account: theontho)",
        "name": "theontho",
        "email": "theontho@users.noreply.github.com",
        "login": "theontho",
        "active": True,
    }

    with patch("scripts.dev_register.subprocess.run") as run:
        configure_git_identity(identity)

    run.assert_any_call(["git", "config", "user.name", "theontho"], check=True)
    run.assert_any_call(
        ["git", "config", "user.email", "theontho@users.noreply.github.com"], check=True
    )
