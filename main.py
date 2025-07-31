from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess
import os

WATCH_PATH = r"C:\Users\rizwa\Tech\Github"

class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if not event.is_directory:
            print(f"Change detected in: {event.src_path}")

            # Detect which repo the change belongs to (top-level folder)
            relative_path = os.path.relpath(event.src_path, WATCH_PATH)
            repo_name = relative_path.split(os.sep)[0]  # First folder name is repo
            repo_path = os.path.join(WATCH_PATH, repo_name)

            print(f"Running git automation for repo: {repo_path}")
            subprocess.run(["python", "git_automation.py", repo_path], cwd=os.path.dirname(__file__))

if __name__ == "__main__":
    observer = Observer()
    event_handler = ChangeHandler()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    observer.start()

    print(f"Watching for changes in: {WATCH_PATH}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
