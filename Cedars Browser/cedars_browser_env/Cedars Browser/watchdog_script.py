import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_script()

    def start_script(self):
        if self.process:
            self.process.kill()
        self.process = subprocess.Popen([sys.executable, self.script])

    def on_any_event(self, event):
        if event.src_path.endswith('.py'):
            print(f"{event.src_path} changed, restarting script...")
            self.start_script()

if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(__file__), 'Cedars_Browser.py')  # Ensure this path is correct
    event_handler = ChangeHandler(script_path)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
