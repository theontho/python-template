import subprocess
from pathlib import Path

def get_git_config(key):
    try:
        return subprocess.check_output(["git", "config", key]).decode().strip()
    except subprocess.CalledProcessError:
        return ""

def register():
    current_name = get_git_config("user.name")
    current_email = get_git_config("user.email")

    print(f"Current Git Identity: {current_name} <{current_email}>")
    confirm = input("Register this identity in .dev_id? (y/n): ")
    if confirm.lower() == 'y':
        with open(".dev_id", "w") as f:
            f.write(f"name={current_name}\n")
            f.write(f"email={current_email}\n")
        print("✅ Registered in .dev_id")
    else:
        print("Registration cancelled.")

if __name__ == "__main__":
    register()
