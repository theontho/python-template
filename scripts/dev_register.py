import subprocess
import json
import sys
from pathlib import Path

def get_git_config(key):
    try:
        return subprocess.check_output(["git", "config", key], stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        return ""

def get_gh_identity():
    try:
        # Check if gh is installed and authenticated
        subprocess.check_output(["gh", "--version"], stderr=subprocess.DEVNULL)
        user_info_raw = subprocess.check_output(["gh", "api", "user"], stderr=subprocess.DEVNULL).decode()
        user_info = json.loads(user_info_raw)
        return {
            "name": user_info.get("name") or user_info.get("login"),
            "email": user_info.get("email") or f"{user_info.get('login')}@users.noreply.github.com",
            "login": user_info.get("login")
        }
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return None

def register():
    identities = []
    
    # Local Git Identity
    git_name = get_git_config("user.name")
    git_email = get_git_config("user.email")
    if git_name or git_email:
        identities.append({
            "source": "Local Git Config",
            "name": git_name,
            "email": git_email
        })

    # GitHub Identity
    gh_id = get_gh_identity()
    if gh_id:
        identities.append({
            "source": f"GitHub (via gh CLI: {gh_id['login']})",
            "name": gh_id["name"],
            "email": gh_id["email"]
        })

    if not identities:
        print("❌ No git or GitHub identity found. Please configure git or login to gh.")
        sys.exit(1)

    print("Available Identities:")
    for i, identity in enumerate(identities, 1):
        print(f"{i}) {identity['source']}: {identity['name']} <{identity['email']}>")

    choice = input(f"Choose an identity to register in .dev_id (1-{len(identities)}) [1]: ") or "1"
    try:
        selected = identities[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        sys.exit(1)

    with open(".dev_id", "w") as f:
        f.write(f"name={selected['name']}\n")
        f.write(f"email={selected['email']}\n")
    
    print(f"✅ Registered in .dev_id using {selected['source']}")

if __name__ == "__main__":
    register()
