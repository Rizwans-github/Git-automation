import git
import os
import sys
import re
import subprocess

if len(sys.argv) > 1:
    REPO_PATH = sys.argv[1]
else:
    raise ValueError("No repository path provided!")

def generate_commit_message(repo):
    # Get the staged changes
    diff = repo.git.diff("--cached")

    if not diff.strip():
        return "chore: no staged changes found"

    prompt = (
        "Generate ONLY a concise Git commit message for the following diff. "
        "Do NOT explain. Do NOT add anything else."
    )

    try:
        result = subprocess.run(
            ["ollama", "run", "qwen3:8b"],
            input=f"{prompt}\n\n{diff}",
            text=True,
            capture_output=True,
            check=True
        )
        commit_message = result.stdout.strip().splitlines()[-1]  # last line only
        return commit_message or "chore: update project files"
    except Exception as e:
        print(f"Ollama error: {e}")
        return "chore: update project files"

def automate_git_commit():
    repo = git.Repo(REPO_PATH)

    if repo.is_dirty(untracked_files=True):
        print(f"Changes detected in {REPO_PATH}, staging files...")
        repo.git.add(A=True)

        commit_msg = generate_commit_message(repo)
        print(f"AI Commit message: {commit_msg}")

        repo.git.commit("-m", commit_msg)

        current_branch = repo.active_branch.name
        print(f"Pushing changes to branch: {current_branch}")
        repo.git.push("origin", current_branch)

        print(" Changes committed and pushed successfully!")
    else:
        print(f"No changes detected in {REPO_PATH}.")

if __name__ == "__main__":
    automate_git_commit()
