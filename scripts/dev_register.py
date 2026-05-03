import json
import re
import subprocess
import sys


def get_git_config(key):
    try:
        return (
            subprocess.check_output(["git", "config", key], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        return ""


def get_gh_identities():
    identities = []
    try:
        # Check if gh is installed
        subprocess.check_output(["gh", "--version"], stderr=subprocess.DEVNULL)

        # Get all logged in accounts
        status_output = subprocess.check_output(
            ["gh", "auth", "status"], stderr=subprocess.STDOUT
        ).decode()

        # Regex to find usernames: "Logged in to <host> account <username>"
        usernames = re.findall(r"Logged in to .+ account ([^\s\(]+)", status_output)

        for username in set(usernames):  # Use set to avoid duplicates if any
            try:
                user_info_raw = subprocess.check_output(
                    ["gh", "api", f"users/{username}"], stderr=subprocess.DEVNULL
                ).decode()
                user_info = json.loads(user_info_raw)
                identities.append(
                    {
                        "source": f"GitHub (account: {username})",
                        "name": user_info.get("name") or user_info.get("login"),
                        "email": user_info.get("email")
                        or f"{user_info.get('login')}@users.noreply.github.com",
                        "login": user_info.get("login"),
                    }
                )
            except Exception:
                # Fallback if API call fails
                identities.append(
                    {
                        "source": f"GitHub (account: {username} - details unavailable)",
                        "name": username,
                        "email": f"{username}@users.noreply.github.com",
                        "login": username,
                    }
                )

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return identities


def register():
    all_identities = []

    # Local Git Identity
    git_name = get_git_config("user.name")
    git_email = get_git_config("user.email")
    if git_name or git_email:
        all_identities.append({"source": "Local Git Config", "name": git_name, "email": git_email})

    # GitHub Identities
    all_identities.extend(get_gh_identities())

    if not all_identities:
        print("❌ No git or GitHub identity found. Please configure git or login to gh.")
        sys.exit(1)

    print("Available Identities:")
    for i, identity in enumerate(all_identities, 1):
        print(f"{i}) {identity['source']}: {identity['name']} <{identity['email']}>")

    choice = (
        input(f"Choose an identity to register in .dev_id (1-{len(all_identities)}) [1]: ") or "1"
    )
    try:
        selected = all_identities[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        sys.exit(1)

    with open(".dev_id", "w") as f:
        f.write(f"name={selected['name']}\n")
        f.write(f"email={selected['email']}\n")

    print(f"✅ Registered in .dev_id using {selected['source']}")


if __name__ == "__main__":
    register()
