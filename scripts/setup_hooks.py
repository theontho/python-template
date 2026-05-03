import subprocess
from pathlib import Path


def setup_hooks() -> None:
    git_dir = Path(".git")
    if not git_dir.exists():
        print("Error: .git directory not found. Are you in the project root?")
        return

    subprocess.run(["uv", "run", "pre-commit", "install"], check=True)
    subprocess.run(["uv", "run", "pre-commit", "install", "--hook-type", "pre-push"], check=True)
    print("Installed pre-commit and pre-push hooks")

    verify_dev_hook = Path(".git/hooks/pre-commit")
    if verify_dev_hook.exists():
        print("Developer identity verification is installed through pre-commit")


if __name__ == "__main__":
    setup_hooks()
