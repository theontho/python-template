import argparse
import json
import re
import subprocess
import sys
from typing import TypedDict


class Identity(TypedDict):
    source: str
    name: str
    email: str
    login: str
    active: bool


def get_git_config(key: str) -> str:
    try:
        return (
            subprocess.check_output(["git", "config", key], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        return ""


def parse_gh_accounts(status_output: str) -> list[tuple[str, bool]]:
    """Return GitHub CLI accounts with the active account first when known."""
    accounts: list[str] = []
    active_account: str | None = None
    current_account: str | None = None

    for line in status_output.splitlines():
        account_match = re.search(r"Logged in to .+ account ([^\s\(]+)", line)
        if account_match:
            current_account = account_match.group(1)
            if current_account not in accounts:
                accounts.append(current_account)
            continue

        active_match = re.search(r"Active account:\s*true", line)
        if active_match and current_account:
            active_account = current_account

    if active_account is None:
        return [(account, False) for account in accounts]

    ordered_accounts = [
        active_account,
        *(account for account in accounts if account != active_account),
    ]
    return [(account, account == active_account) for account in ordered_accounts]


def get_gh_identities() -> list[Identity]:
    identities: list[Identity] = []
    try:
        # Check if gh is installed
        subprocess.check_output(["gh", "--version"], stderr=subprocess.DEVNULL)

        # Get all logged in accounts
        status_output = subprocess.check_output(
            ["gh", "auth", "status"], stderr=subprocess.STDOUT
        ).decode()

        for username, active in parse_gh_accounts(status_output):
            try:
                user_info_raw = subprocess.check_output(
                    ["gh", "api", f"users/{username}"], stderr=subprocess.DEVNULL
                ).decode()
                user_info = json.loads(user_info_raw)
                login = str(user_info.get("login") or username)
                source = (
                    f"GitHub (active account: {username})"
                    if active
                    else f"GitHub (account: {username})"
                )
                identities.append(
                    {
                        "source": source,
                        "name": login,
                        "email": user_info.get("email") or f"{login}@users.noreply.github.com",
                        "login": login,
                        "active": active,
                    }
                )
            except Exception:
                # Fallback if API call fails
                source = (
                    f"GitHub (active account: {username} - details unavailable)"
                    if active
                    else f"GitHub (account: {username} - details unavailable)"
                )
                identities.append(
                    {
                        "source": source,
                        "name": username,
                        "email": f"{username}@users.noreply.github.com",
                        "login": username,
                        "active": active,
                    }
                )

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return identities


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register the expected developer identity")
    parser.add_argument(
        "--choice",
        type=int,
        default=None,
        help="Identity number to register. Defaults to the active GitHub account when available.",
    )
    parser.add_argument(
        "--no-update-git-config",
        action="store_true",
        help="Only write .dev_id; do not update this repository's git user.name/user.email.",
    )
    return parser.parse_args()


def default_choice(all_identities: list[Identity]) -> int:
    for index, identity in enumerate(all_identities, 1):
        if identity["active"]:
            return index
    return 1


def choose_identity(all_identities: list[Identity], choice: int | None) -> Identity:
    default = default_choice(all_identities)
    if choice is None:
        if sys.stdin.isatty():
            raw_choice = input(
                f"Choose an identity to register in .dev_id (1-{len(all_identities)}) [{default}]: "
            ) or str(default)
            try:
                choice = int(raw_choice)
            except ValueError:
                print("Invalid choice.")
                sys.exit(1)
        else:
            choice = default

    if choice < 1:
        print("Invalid choice.")
        sys.exit(1)

    try:
        return all_identities[choice - 1]
    except IndexError:
        print("Invalid choice.")
        sys.exit(1)


def configure_git_identity(identity: Identity) -> None:
    subprocess.run(["git", "config", "user.name", identity["name"]], check=True)
    subprocess.run(["git", "config", "user.email", identity["email"]], check=True)


def register() -> None:
    args = parse_args()
    all_identities: list[Identity] = []

    # GitHub identities first so the active gh account is the default choice.
    all_identities.extend(get_gh_identities())

    # Local Git Identity
    git_name = get_git_config("user.name")
    git_email = get_git_config("user.email")
    if git_name or git_email:
        all_identities.append(
            {
                "source": "Local Git Config",
                "name": git_name,
                "email": git_email,
                "login": "",
                "active": False,
            }
        )

    if not all_identities:
        print("No git or GitHub identity found. Please configure git or login to gh.")
        sys.exit(1)

    print("Available Identities:")
    for i, identity in enumerate(all_identities, 1):
        print(f"{i}) {identity['source']}: {identity['name']} <{identity['email']}>")

    selected = choose_identity(all_identities, args.choice)

    with open(".dev_id", "w") as f:
        f.write(f"name={selected['name']}\n")
        f.write(f"email={selected['email']}\n")

    print(f"Registered in .dev_id using {selected['source']}")
    if not args.no_update_git_config:
        configure_git_identity(selected)
        print("Updated repository git identity to match .dev_id")


if __name__ == "__main__":
    register()
