import git
import os
import sys
import subprocess

# Set repository path from command line argument
if len(sys.argv) > 1:
    REPO_PATH = sys.argv[1]
else:
    REPO_PATH = r"C:\Users\rizwa\Tech\Github\Git-automation"  # fallback path

OLLAMA_PATH = r"C:\Users\rizwa\AppData\Local\Programs\Ollama\ollama app.exe"  # Ollama executable path

def generate_commit_message(repo):
    changed_files = repo.git.diff("--cached", "--name-only").splitlines()
    diff_summary = repo.git.diff("--cached", "--unified=3")

    if not changed_files:
        return "chore: no significant changes"

    files_list = "\n".join(changed_files)
    prompt = (
        f"You are an AI specialized in generating meaningful git commit messages.\n"
        f"Analyze the following staged changes and return ONLY one commit message.\n\n"
        f"Rules:\n"
        f"- Use conventional commit style (feat, fix, chore, refactor, docs, test, style)\n"
        f"- Mention the file or feature if possible\n"
        f"- Do NOT add explanations or anything else\n\n"
        f"Changed files:\n{files_list}\n\n"
        f"Diff:\n{diff_summary}\n\n"
        f"Output ONLY the commit message:"
    )

    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", "codellama:7b"],
            input=prompt,
            text=True,
            capture_output=True
        )

        if result.returncode == 0 and result.stdout.strip():
            raw_output = result.stdout.strip()
            print("Raw Ollama output:", raw_output)  # ✅ Removed emoji
            return raw_output.split("\n")[0]  # Only the first line

    except Exception as e:
        print(f"Ollama error: {e}")

    return f"chore({changed_files[0]}): update project files" if changed_files else "chore: update project files"

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
