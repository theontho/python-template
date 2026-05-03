import subprocess
import sys
from pathlib import Path


def get_git_config(key):
    try:
        return subprocess.check_output(["git", "config", key]).decode().strip()
    except subprocess.CalledProcessError:
        return None


def verify():
    dev_id_path = Path(".dev_id")
    if not dev_id_path.exists():
        print("❌ Error: .dev_id file not found!")
        print("Please run 'python-template dev-register' to set up your identity.")
        sys.exit(1)

    expected = {}
    with open(dev_id_path) as f:
        for line in f:
            if "=" in line:
                k, v = line.split("=", 1)
                expected[k.strip()] = v.strip()

    current_name = get_git_config("user.name")
    current_email = get_git_config("user.email")

    errors = []
    if current_name != expected.get("name"):
        errors.append(f"Expected name '{expected.get('name')}', found '{current_name}'")
    if current_email != expected.get("email"):
        errors.append(f"Expected email '{expected.get('email')}', found '{current_email}'")

    if errors:
        print("❌ Git identity mismatch!")
        for err in errors:
            print(f"  - {err}")
        print("\nPlease update your git config or .dev_id file.")
        sys.exit(1)

    print("✅ Git identity verified.")


if __name__ == "__main__":
    verify()
