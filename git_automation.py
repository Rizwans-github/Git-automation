import git
import os
import sys
import subprocess

if len(sys.argv) > 1:
    REPO_PATH = sys.argv[1]
else:
    raise ValueError("No repository path provided!")

def generate_commit_message(repo):
    # Get staged changes (diff and file names)
    changed_files = repo.git.diff("--cached", "--name-only").splitlines()
    diff_summary = repo.git.diff("--cached", "--unified=0")  # Only changed lines

    if not changed_files:
        return "chore: no significant changes"

    files_list = "\n".join(changed_files)
    prompt = f"""
    You are an expert developer.
    Analyze the following git changes and generate a clear and concise commit message.

    Changed files:
    {files_list}

    Diff:
    {diff_summary}

    Commit message:
    """

    try:
        result = subprocess.run(
            ["ollama", "run", "codellama:7b"],
            input=prompt,
            text=True,
            capture_output=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"⚠️ Ollama error: {e}")

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

        print("✅ Changes committed and pushed successfully!")
    else:
        print(f"No changes detected in {REPO_PATH}.")

if __name__ == "__main__":
    automate_git_commit()
