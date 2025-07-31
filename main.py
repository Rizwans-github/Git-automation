from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess
import os

WATCH_PATH = r"C:\Users\rizwa\Tech\Github"

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_event = None
        self.last_time = 0

    def on_any_event(self, event):
        if event.is_directory:
            return

        # Ignore .git folder and hidden files
        if ".git" in event.src_path or event.src_path.endswith("~"):
            return

        # Debounce duplicate events (avoid multiple triggers in <2 sec)
        current_time = time.time()
        if self.last_event == event.src_path and (current_time - self.last_time) < 2:
            return

        self.last_event = event.src_path
        self.last_time = current_time

        print(f"Change detected in: {event.src_path}")

        # Detect repo name from path
        relative_path = os.path.relpath(event.src_path, WATCH_PATH)
        repo_name = relative_path.split(os.sep)[0]
        repo_path = os.path.join(WATCH_PATH, repo_name)

        print(f"Running git automation for repo: {repo_path}")
        subprocess.run(["python", "git_automation.py", repo_path], cwd=os.path.dirname(__file__))

if __name__ == "__main__":
    observer = Observer()
    event_handler = ChangeHandler()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    observer.start()

    print(f"✅ Watching for changes in: {WATCH_PATH}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
