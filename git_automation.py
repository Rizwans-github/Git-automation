import git
import os
import sys
import subprocess

if len(sys.argv) > 1:
    BASE_PATH = sys.argv[1]
else:
    raise ValueError("No base path provided!")

def generate_commit_message(repo):
    """Generate commit message using mistral:7b-instruct via Ollama."""
    diff = repo.git.diff("--cached")
    if not diff.strip():
        return "chore: no staged changes found"

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral:7b-instruct"],
            input=(
                f"Output ONLY a single Git commit message of one line. "
                f"DO NOT include anything else. DO NOT add explanations, examples, ```diff, "
                f"Proposed commit message:, or any extra text:\n{diff}\n"),
            text=True,
            capture_output=True,
            encoding="utf-8"
        )
        output = result.stdout.strip()

        for line in output.splitlines():
            line = line.strip()
            if line and not line.lower().startswith(("thinking", "okay", "explanation", "this git commit")):
                return line

        return "chore: update project files"

    except Exception as e:
        print(f"Ollama error: {e}")
        return "chore: update project files"

def process_repo(repo_path):
    try:
        repo = git.Repo(repo_path)

        if repo.is_dirty(untracked_files=True):
            print(f"Changes detected in {repo_path}, staging files...")
            repo.git.add(A=True)

            commit_msg = generate_commit_message(repo)
            print(f"\nProposed commit message: {commit_msg}")
            user_input = input("Approve commit? (y/edit/n): ").strip().lower()

            if user_input == "edit":
                commit_msg = input("Enter your commit message: ").strip()
            elif user_input != "y":
                print("❌ Commit aborted.")
                return

            repo.git.commit("-m", commit_msg)
            current_branch = repo.active_branch.name
            print(f"Pushing changes to branch: {current_branch}")
            repo.git.push("origin", current_branch)
            print("✅ Changes committed and pushed successfully!\n")
        else:
            print(f"No changes detected in {repo_path}.\n")

    except git.exc.InvalidGitRepositoryError:
        # Skip non-git folders
        return

def automate_git_commit():
    for root, dirs, _ in os.walk(BASE_PATH):
        if ".git" in dirs:  # Check if this folder is a repo
            process_repo(root)
            dirs[:] = []  # Do not go deeper once a repo is found

if __name__ == "__main__":
    automate_git_commit()
