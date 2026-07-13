import schedule
import time
import subprocess
import logging
from pathlib import Path
import os
import shutil
import sys
from scripts.audit_logger import get_audit_logger

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
audit = get_audit_logger('orchestrator')

VAULT_PATH = Path(os.getenv('VAULT_PATH', 'D:/Hackathon0/AI_Employee_Vault'))
SCRIPTS_DIR = Path(os.getenv('SCRIPTS_DIR', 'D:/Hackathon0/scripts'))

def run_claude_task(task_description):
    """Execute a simple, single-step Claude Code task"""
    logger.info(f"Running simple task: {task_description[:50]}...")
    audit.log_action('claude_simple_task', 'system', {'description': task_description[:100]}, status='started')
    try:
        if shutil.which('claude'):
            # Run Claude directly
            result = subprocess.run(
                ['claude', '--cwd', str(VAULT_PATH), task_description],
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                logger.info("Simple task completed successfully.")
                audit.log_action('claude_simple_task', 'system', {'description': task_description[:100]}, status='success')
                return True
            else:
                logger.error(f"Task failed: {result.stderr}")
                audit.log_action('claude_simple_task', 'system', {'description': task_description[:100], 'error': result.stderr}, status='failure')
                return False
        else:
            logger.warning("Claude CLI not found. Simulating task execution.")
            audit.log_action('claude_simple_task', 'system', {'description': task_description[:100]}, status='simulated')
            return True
    except Exception as e:
        logger.error(f"Failed to run task: {e}")
        audit.log_action('claude_simple_task', 'system', {'error': str(e)}, status='failure')
        return False

def run_ralph_loop(task_id, prompt):
    """Execute a complex task using the Ralph Loop pattern"""
    logger.info(f"Starting Ralph Loop for task: {task_id}")
    try:
        ralph_script = SCRIPTS_DIR / 'ralph_loop.py'
        if not ralph_script.exists():
            logger.error(f"Ralph loop script not found at {ralph_script}")
            return False
            
        # Run the python script
        # We run it as a subprocess to avoid blocking the scheduler forever, 
        # but for now we'll block to ensure completion before taking next job.
        # In production -> async or separate thread.
        cmd = [sys.executable, str(ralph_script), task_id, prompt, '--max', '10']
        
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True, # We might want to stream this to logs instead
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            logger.info(f"Ralph Loop completed for {task_id}")
            return True
        else:
            logger.error(f"Ralph Loop failed for {task_id}: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Failed to run Ralph Loop: {e}")
        return False

def process_needs_action():
    """Check /Needs_Action and process pending tasks"""
    needs_action = VAULT_PATH / 'Needs_Action'
    if not needs_action.exists(): return

    for file in needs_action.glob('*.md'):
        try:
            content = file.read_text(encoding='utf-8')
            
            # Skip if not pending or already being processed
            if 'status: pending' not in content:
                continue
                
            task_id = file.stem
            logger.info(f"Found pending task: {task_id}")
            
            # Mark as in_progress to avoid double processing
            # In a real DB we'd update a row. Here we can rename or update file.
            # For this prototype, we'll just run it.
            
            # Heuristic for Complex Tasks:
            # If it's a file drop (generic) or explicitly asks for a plan, use Ralph.
            # Simple tasks like "Summarize this" might be simple.
            # Gold Tier Rule: Default to Ralph for robustness.
            
            prompt = f"Process the file '{file.name}'. Content:\n{content}"
            success = run_ralph_loop(task_id, prompt)
            
            if success:
                # Move to Done
                done_dir = VAULT_PATH / 'Done'
                done_dir.mkdir(exist_ok=True)
                shutil.move(str(file), str(done_dir / file.name))
                logger.info(f"Moved {file.name} to Done")
                
                # Update Dashboard
                update_dashboard()
                
        except Exception as e:
            logger.error(f"Error processing file {file}: {e}")

def check_approvals():
    """Check if any files moved to /Approved and execute them"""
    approved = VAULT_PATH / 'Approved'
    if not approved.exists(): return

    for file in approved.glob('*.md'):
        try:
            content = file.read_text(encoding='utf-8')
            if 'type: linkedin_post' in content or 'type: linkedin_feed_item' in content:
                continue # Handled by watchers
            
            logger.info(f"Found approved action: {file.name}")
            
            # Approved actions are usually "Execute this now". 
            # We can use simple Claude task or Ralph if it's complex.
            # Let's use simple for approvals.
            run_claude_task(
                f"Read {file} and execute the approved action using tools. "
                f"Then move the file to /Done."
            )
        except Exception as e:
            logger.error(f"Error checking approvals: {e}")

def generate_linkedin_post():
    logger.info("Generating LinkedIn post...")
    run_claude_task(
        "Use the post_to_linkedin skill to create a new LinkedIn post draft."
    )

def update_dashboard():
    logger.info("Updating dashboard...")
    run_claude_task(
        "Update Dashboard.md with current status of Needs_Action, Done, and Logs."
    )

# Schedule
schedule.every(60).seconds.do(process_needs_action) # Updated to 60s
schedule.every(2).minutes.do(check_approvals)
schedule.every(10).minutes.do(update_dashboard)
schedule.every().monday.at("09:00").do(generate_linkedin_post)
schedule.every().thursday.at("09:00").do(generate_linkedin_post)

logger.info("Gold Tier Orchestrator started.")

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
