import time
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is optional for local runs
    def load_dotenv(*args, **kwargs):
        return False

# Load environment variables
load_dotenv()

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
DROP_FOLDER = Path('./Drop_Folder')
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'



from scripts.retry_handler import with_retry, TransientError
from scripts.audit_logger import get_audit_logger

audit = get_audit_logger('filesystem_watcher')

@with_retry(max_attempts=3, exceptions=(OSError, PermissionError))
def safe_action(description, fn):
    if DRY_RUN:
        print(f"[DRY RUN] Would: {description}")
        return
    fn()

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        # Add a small delay to ensure file is fully written
        time.sleep(1)
        
        self.process_file(Path(event.src_path))

    @with_retry(max_attempts=3, backoff_factor=1.5)
    def process_file(self, file_path):
        print(f"Detected new file: {file_path}")
        
        filename = file_path.name
        target_path = NEEDS_ACTION / filename
        metadata_path = NEEDS_ACTION / f"{filename}.md"
        
        # Log discovery
        audit.log_action('file_detect', filename, {'path': str(file_path)}, status='success')
        
        # Prepare metadata
        file_stats = file_path.stat()
        metadata_content = f"""---
type: file_drop
original_name: {filename}
size: {file_stats.st_size}
dropped_at: {datetime.now().isoformat()}
status: pending
---
New file dropped for processing. Review and decide action.
"""

        def move_and_create_metadata():
            # Move the file
            shutil.move(str(file_path), str(target_path))
            print(f"Moved {filename} to {NEEDS_ACTION}")
            
            # Create metadata file
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(metadata_content)
            print(f"Created metadata at {metadata_path}")
            
            # Log action
            audit.log_action('file_move', filename, {'from': str(file_path), 'to': str(target_path)}, status='success')

        safe_action(f"Move {filename} to Needs_Action and create metadata", move_and_create_metadata)

def start_watcher():
    # Ensure directories exist
    if not DROP_FOLDER.exists():
        DROP_FOLDER.mkdir(parents=True)
    if not NEEDS_ACTION.exists():
        NEEDS_ACTION.mkdir(parents=True)

    print(f"Monitoring {DROP_FOLDER} for new files...")
    print(f"Target: {NEEDS_ACTION}")
    print(f"Dry Run: {DRY_RUN}")

    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(DROP_FOLDER), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
