import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import get_runtime_paths
from scripts.audit_logger import get_audit_logger

# Configuration
VAULT_PATH, _ = get_runtime_paths()
LOGS_DIR = VAULT_PATH / 'Logs'
DONE_DIR = VAULT_PATH / 'Done'

audit = get_audit_logger('ralph_loop')

def setup_logging():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f'ralph_loop_{date_str}.log'
    return log_file

def log(file_path, message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    entry = f"[{timestamp}] {message}\n"
    print(message)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(entry)

def check_completion(task_id, stdout_content):
    # 1. Check for Promise String in output
    if '<promise>TASK_COMPLETE</promise>' in stdout_content:
        return True, "Promise string found in output."
        
    # 2. Check for Done file
    done_file = DONE_DIR / f"{task_id}.md"
    if done_file.exists():
        return True, f"Done file found: {done_file.name}"
        
    return False, "Completion criteria not met."


def run_loop(task_id, prompt, max_iterations=10):
    log_file = setup_logging()
    
    audit.log_action('ralph_loop_start', task_id, {'prompt': prompt, 'max_iterations': max_iterations}, status='started')
    
    log(log_file, f"=== Starting Ralph Loop for Task: {task_id} ===")
    log(log_file, f"Max Iterations: {max_iterations}")
    
    current_iteration = 1
    context = ""
    
    # Ensure dependencies
    skill_path = VAULT_PATH / "Skills" / "autonomous_task" / "SKILL.md"
    if not skill_path.exists():
        log(log_file, "WARNING: autonomous_task skill not found.")

    while current_iteration <= max_iterations:
        log(log_file, f"\n--- Iteration {current_iteration}/{max_iterations} ---")
        
        # Construct the command
        # We inject the autonomous_task skill usage into the prompt
        full_prompt = (
            f"{prompt}\n\n"
            f"CONTEXT FROM PREVIOUS STEPS:\n{context}\n\n"
            f"INSTRUCTION: You are in an autonomous loop (Iteration {current_iteration}). "
            "Use the 'autonomous_task' skill to determine your next step. "
            "If you have finished ALL steps, output <promise>TASK_COMPLETE</promise>."
        )
        
        cmd = ['claude', '--cwd', str(VAULT_PATH), full_prompt]
        
        try:
            # Run Claude
            # Using shell=True for Windows compatibility in some envs, but list usually safer.
            # We use standard subprocess run.
            log(log_file, "Executing Claude...")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='replace' # Handle emoji/unicode issues
            )
            
            output = result.stdout + "\n" + result.stderr
            log(log_file, f"Agent Output Length: {len(output)} chars")
            
            audit.log_action('ralph_loop_iteration', task_id, {'iteration': current_iteration, 'output_len': len(output)}, status='success')
            
            # Update context for next loop
            # We keep the last 2000 chars of output to avoid blowing up context window
            context = f"Last Iteration Output (Snippet):\n{output[-2000:]}"
            
            # Check Stop Hook
            is_done, reason = check_completion(task_id, output)
            
            if is_done:
                log(log_file, f"SUCCESS: {reason}")
                
                # Write Summary
                summary_file = LOGS_DIR / f"ralph_summary_{task_id}.md"
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Task Summary: {task_id}\n")
                    f.write(f"Status: Success\n")
                    f.write(f"Iterations: {current_iteration}\n")
                    f.write(f"Reason: {reason}\n")
                    f.write(f"Completed At: {datetime.now().isoformat()}\n")
                
                audit.log_action('ralph_loop_complete', task_id, {'reason': reason, 'iterations': current_iteration}, status='success')
                return True

            log(log_file, f"Status: Not done ({reason}). looping...")
            
        except Exception as e:
            log(log_file, f"CRITICAL ERROR: {str(e)}")
            audit.log_action('ralph_loop_error', task_id, {'error': str(e)}, status='failure')
            time.sleep(5) # Backoff
            
        current_iteration += 1
        time.sleep(2) # Breath

    log(log_file, "FAILURE: Max iterations reached without completion.")
    audit.log_action('ralph_loop_failed', task_id, {'reason': 'max_iterations_reached'}, status='failure')
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop Runner')
    parser.add_argument('task_id', help='Unique ID of the task (filename without extension)')
    parser.add_argument('prompt', help='The initial prompt/instruction')
    parser.add_argument('--max', type=int, default=10, help='Max iterations')
    
    args = parser.parse_args()
    
    run_loop(args.task_id, args.prompt, args.max)
