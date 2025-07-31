import git
import os
import sys
import subprocess
import re

if len(sys.argv) > 1:
    GITHUB_PATH = sys.argv[1]
else:
    GITHUB_PATH = r"C:\Users\rizwa\Tech\Github"

def generate_commit_message(repo):
    """Generate commit message using mistral:7b-instruct via Ollama."""
    diff = repo.git.diff("--cached")
    if not diff.strip():
        return "chore: no staged changes found"

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral:7b-instruct"],
            input=(
                f"Generate ONLY ONE Git commit message in the format:\n"
                f"<type>: <short description>\n"
                f"Allowed types: feat, fix, chore, docs, refactor, test.\n"
                f"NO explanations, NO extra text, NO ```diff, NO labels.\n\n"
                f"Diff:\n{diff}\n"
            ),
            text=True,
            capture_output=True,
            encoding="utf-8"
        )

        output = result.stdout.strip()

        # Extract valid commit message
        match = re.search(r"(feat|fix|chore|docs|refactor|test): .+", output, re.IGNORECASE)
        if match:
            return match.group(0).strip()

        return "chore: update project files"

    except Exception as e:
        print(f"Ollama error: {e}")
        return "chore: update project files"

def automate_git_commit(repo_path):
    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        print(f"Skipping {repo_path}: Not a git repository.")
        return

    if repo.is_dirty(untracked_files=True):
        print(f"\nChanges detected in {repo_path}, staging files...")
        repo.git.add(A=True)

        commit_msg = generate_commit_message(repo)
        print(f"\nProposed commit message: {commit_msg}")
        user_input = input("Approve commit? (y/edit/n): ").strip().lower()

        if user_input == "n":
            print("❌ Commit aborted.")
            return
        elif user_input == "edit":
            commit_msg = input("Enter your custom commit message: ")

        repo.git.commit("-m", commit_msg)

        current_branch = repo.active_branch.name
        print(f"Pushing changes to branch: {current_branch}")
        repo.git.push("origin", current_branch)
        print("✅ Changes committed and pushed successfully!")
    else:
        print(f"No changes detected in {repo_path}.")

def scan_github_folder():
    for root, dirs, _ in os.walk(GITHUB_PATH):
        if ".git" in dirs:
            automate_git_commit(root)

if __name__ == "__main__":
    scan_github_folder()
