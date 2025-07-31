import git
import os
import sys

# Get repo path dynamically from main.py
if len(sys.argv) > 1:
    REPO_PATH = sys.argv[1]
else:
    raise ValueError("No repository path provided!")

def generate_commit_message(diff):
    # Simple commit message generator (AI-free)
    if "requirements.txt" in diff:
        return "chore: update dependencies"
    elif "README" in diff:
        return "docs: update README"
    elif "test" in diff:
        return "test: update test files"
    else:
        return "chore: update project files"

def automate_git_commit():
    repo = git.Repo(REPO_PATH)

    if repo.is_dirty(untracked_files=True):
        print(f"Changes detected in {REPO_PATH}, staging files...")
        repo.git.add(A=True)

        diff = repo.git.diff('--cached')
        commit_msg = generate_commit_message(diff)
        print(f"Commit message: {commit_msg}")

        repo.git.commit('-m', commit_msg)

        # Detect current branch dynamically
        current_branch = repo.active_branch.name
        print(f"Pushing changes to branch: {current_branch}")

        repo.git.push("origin", current_branch)
        print("✅ Changes committed and pushed successfully!")
    else:
        print(f"No changes detected in {REPO_PATH}.")

if __name__ == "__main__":
    automate_git_commit()
