import git
import os
import sys
import subprocess
import re

if len(sys.argv) > 1:
    REPO_PATH = sys.argv[1]
else:
    raise ValueError("No repository path provided!")

def generate_commit_message(repo):
    """Generate commit message using mistral:7b-instruct model through Ollama."""
    diff = repo.git.diff("--cached")
    if not diff.strip():
        return "chore: no staged changes found"

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral:7b-instruct"],
            input=f"Return ONLY a short Git commit message in this format: <type>: <message>. No explanations.\n{diff}\n",
            text=True,
            capture_output=True,
            encoding="utf-8"
        )
        output = result.stdout.strip()

        # Debugging: print raw Ollama output
        print(f"Ollama raw output:\n{output}\n{'-'*60}")

        # Extract first valid line (ignore explanations or thinking text)
        for line in output.splitlines():
            line = line.strip()
            if line and not re.match(r'^(thinking|okay|explanation|commit message)', line.lower()):
                return line

        return "chore: update project files"

    except Exception as e:
        print(f"Ollama error: {e}")
        return "chore: update project files"


def automate_git_commit():
    if not os.path.exists(os.path.join(REPO_PATH, ".git")):
        print(f"Skipping {REPO_PATH}: Not a git repository.")
        return

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

        print("✅ Changes committed and pushed successfully!")
    else:
        print(f"No changes detected in {REPO_PATH}.")

if __name__ == "__main__":
    automate_git_commit()
