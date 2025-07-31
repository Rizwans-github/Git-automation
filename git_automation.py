import git
from openai import OpenAI
from dotenv import load_dotenv
import os
import sys

# Load .env file
load_dotenv(dotenv_path=r"C:\Users\rizwa\Tech\Github\automation\.env")

# Get repo path from main.py
if len(sys.argv) > 1:
    REPO_PATH = sys.argv[1]
else:
    raise ValueError("No repository path provided!")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def automate_git_commit():
    repo = git.Repo(REPO_PATH)

    if repo.is_dirty(untracked_files=True):
        print(f"Changes detected in {REPO_PATH}, staging files...")
        repo.git.add(A=True)

        diff = repo.git.diff('--cached')

        print("Generating commit message with ChatGPT...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes clear, concise git commit messages."},
                {"role": "user", "content": f"Generate a commit message for this diff:\n{diff}"}
            ]
        )

        commit_msg = response.choices[0].message.content.strip()
        print(f"Commit message: {commit_msg}")

        repo.git.commit('-m', commit_msg)
        repo.git.push()

        print("Changes committed and pushed successfully!")
    else:
        print(f"No changes detected in {REPO_PATH}.")

if __name__ == "__main__":
    automate_git_commit()
