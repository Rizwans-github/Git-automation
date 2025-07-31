import git
import os
import sys
import re

if len(sys.argv) > 1:
    REPO_PATH = sys.argv[1]
else:
    raise ValueError("No repository path provided!")

def generate_commit_message(repo):
    staged_files = [item.a_path for item in repo.index.diff("HEAD")]  # changed files
    diff = repo.git.diff("--cached")

    message_parts = []

    for file in staged_files:
        if file.endswith(".py"):
            message_parts.append(f"refactor: update {file}")
        elif file.endswith(".md"):
            message_parts.append(f"docs: update {file}")
        elif file == "requirements.txt":
            message_parts.append("chore: update dependencies")
        else:
            message_parts.append(f"chore: modify {file}")

    # Analyze diff for keywords
    if re.search(r"def |class ", diff):
        message_parts.insert(0, "feat: add/update functions or classes")
    if re.search(r"fix|bug", diff, re.IGNORECASE):
        message_parts.insert(0, "fix: bug fix in code")

    return " | ".join(message_parts)

def automate_git_commit():
    repo = git.Repo(REPO_PATH)

    if repo.is_dirty(untracked_files=True):
        print(f"Changes detected in {REPO_PATH}, staging files...")
        repo.git.add(A=True)

        commit_msg = generate_commit_message(repo)
        print(f"Commit message: {commit_msg}")

        repo.git.commit("-m", commit_msg)

        current_branch = repo.active_branch.name
        print(f"Pushing changes to branch: {current_branch}")
        repo.git.push("origin", current_branch)

        print("✅ Changes committed and pushed successfully!")
    else:
        print(f"No changes detected in {REPO_PATH}.")

if __name__ == "__main__":
    automate_git_commit()