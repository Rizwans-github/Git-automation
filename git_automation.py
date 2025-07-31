import git
import os
import sys
import subprocess

if len(sys.argv) > 1:
    ROOT_PATH = sys.argv[1]  # e.g. C:\Users\rizwa\Tech\Github
else:
    raise ValueError("No repository path provided!")

def generate_commit_message(repo):
    diff = repo.git.diff("--cached")
    if not diff.strip():
        return "chore: no staged changes found"

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral:7b-instruct"],
            input=f"Output ONLY a single Git commit message (no explanations):\n{diff}\n",
            text=True,
            capture_output=True,
            encoding="utf-8"
        )
        output = result.stdout.strip()

        for line in output.splitlines():
            line = line.strip()
            if line and not line.lower().startswith(("thinking", "okay", "explanation", "commit message")):
                return line

        return "chore: update project files"

    except Exception as e:
        print(f"Ollama error: {e}")
        return "chore: update project files"

def process_repository(repo_path):
    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        return  # Skip folders that are not git repos

    if repo.is_dirty(untracked_files=True):
        print(f"Changes detected in {repo_path}, staging files...")
        repo.git.add(A=True)

        commit_msg = generate_commit_message(repo)
        print(f"AI Commit message: {commit_msg}")

        repo.git.commit("-m", commit_msg)
        current_branch = repo.active_branch.name
        print(f"Pushing changes to branch: {current_branch}")
        repo.git.push("origin", current_branch)

        print("✅ Changes committed and pushed successfully!")

def automate_git_commit():
    # Loop through all folders in the ROOT_PATH
    for dirpath, dirnames, filenames in os.walk(ROOT_PATH):
        if ".git" in dirnames:  # if it's a git repo
            process_repository(dirpath)
            dirnames.clear()  # prevent descending into .git folder

if __name__ == "__main__":
    automate_git_commit()
