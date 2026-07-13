import logging
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import schedule

from config import get_runtime_paths
from scripts.audit_logger import get_audit_logger
from scripts.retry_handler import TransientError, with_retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
audit = get_audit_logger('orchestrator')

VAULT_PATH, SCRIPTS_DIR = get_runtime_paths()
WORKER_ID = os.getenv('WORKER_ID', 'orchestrator')
MAX_RALPH_WORKERS = max(1, int(os.getenv('MAX_RALPH_WORKERS', '3')))
CLAUDE_TIMEOUT_SECONDS = max(30, int(os.getenv('CLAUDE_TIMEOUT_SECONDS', '300')))

def _workflow_directories() -> tuple[Path, Path, Path, Path, Path]:
    needs_action_dir = VAULT_PATH / 'Needs_Action'
    approved_dir = VAULT_PATH / 'Approved'
    in_progress_dir = VAULT_PATH / 'In_Progress' / WORKER_ID
    done_dir = VAULT_PATH / 'Done'
    blocked_dir = VAULT_PATH / 'Blocked'

    for directory in (needs_action_dir, approved_dir, in_progress_dir, done_dir, blocked_dir):
        directory.mkdir(parents=True, exist_ok=True)

    return needs_action_dir, approved_dir, in_progress_dir, done_dir, blocked_dir


NEEDS_ACTION_DIR, APPROVED_DIR, IN_PROGRESS_DIR, DONE_DIR, BLOCKED_DIR = _workflow_directories()
TASK_EXECUTOR = ThreadPoolExecutor(max_workers=MAX_RALPH_WORKERS)
PENDING_TASKS: dict[Path, object] = {}


def _ensure_runtime_prerequisites() -> None:
    claude_path = shutil.which('claude')
    if not claude_path:
        raise RuntimeError(
            'Missing required CLI dependency: claude. Install the Claude CLI and ensure it is on PATH before starting the orchestrator.'
        )

    ralph_script = SCRIPTS_DIR / 'ralph_loop.py'
    if not ralph_script.exists():
        raise FileNotFoundError(
            f'Missing Ralph Loop script at {ralph_script}. '
            'Set SCRIPTS_DIR to the directory that contains ralph_loop.py.'
        )


@with_retry(max_attempts=3, base_delay=1, max_delay=30, backoff_factor=2, exceptions=(TransientError,))
def _run_subprocess(cmd: list[str], timeout_seconds: int = 300) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            encoding='utf-8',
            errors='replace',
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TransientError(f'Command timed out after {timeout_seconds}s: {cmd}') from exc
    except OSError as exc:
        raise TransientError(f'Unable to execute command {cmd}: {exc}') from exc


def _move_to_folder(source: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source.name
    source.rename(destination)
    return destination


def claim_task(task_file: Path) -> Path | None:
    _, _, in_progress_dir, _, _ = _workflow_directories()
    target_path = in_progress_dir / task_file.name
    try:
        claimed_path = task_file.rename(target_path)
        logger.info('Claimed task %s by moving it into %s', task_file.name, claimed_path)
        return Path(claimed_path)
    except OSError as exc:
        logger.warning('Unable to claim task %s: %s', task_file.name, exc)
        return None


def run_claude_task(task_description, task_file: Path | None = None):
    """Execute a simple, single-step Claude Code task."""
    logger.info('Running simple task: %s...', task_description[:50])
    audit.log_action('claude_simple_task', 'system', {'description': task_description[:100]}, status='started')

    if not shutil.which('claude'):
        logger.error('Claude CLI is not available on PATH. Blocking the task instead of silently succeeding.')
        audit.log_action(
            'claude_simple_task',
            'system',
            {'description': task_description[:100]},
            status='blocked',
            result='claude_cli_missing',
        )
        if task_file is not None:
            _move_to_folder(task_file, BLOCKED_DIR)
        return False

    try:
        result = _run_subprocess(
            ['claude', '--cwd', str(VAULT_PATH), task_description],
            timeout_seconds=CLAUDE_TIMEOUT_SECONDS,
        )
        if result.returncode == 0:
            logger.info('Simple task completed successfully.')
            audit.log_action('claude_simple_task', 'system', {'description': task_description[:100]}, status='success')
            return True

        logger.error('Task failed: %s', result.stderr.strip())
        audit.log_action(
            'claude_simple_task',
            'system',
            {'description': task_description[:100], 'error': result.stderr.strip()},
            status='failure',
        )
        if task_file is not None:
            _move_to_folder(task_file, BLOCKED_DIR)
        return False
    except Exception as exc:
        logger.error('Failed to run task: %s', exc)
        audit.log_action('claude_simple_task', 'system', {'error': str(exc)}, status='failure')
        if task_file is not None:
            _move_to_folder(task_file, BLOCKED_DIR)
        return False


def run_ralph_loop(task_id, prompt):
    """Execute a complex task using the Ralph Loop pattern."""
    logger.info('Starting Ralph Loop for task: %s', task_id)
    ralph_script = SCRIPTS_DIR / 'ralph_loop.py'
    if not ralph_script.exists():
        logger.error('Ralph loop script not found at %s', ralph_script)
        return False

    try:
        cmd = [sys.executable, str(ralph_script), task_id, prompt, '--max', '10']
        result = _run_subprocess(cmd, timeout_seconds=1200)
        if result.returncode == 0:
            logger.info('Ralph Loop completed for %s', task_id)
            return True

        logger.error('Ralph Loop failed for %s: %s', task_id, result.stderr.strip())
        return False
    except Exception as exc:
        logger.error('Failed to run Ralph Loop: %s', exc)
        return False


def _handle_completed_future(future, claimed_file: Path) -> None:
    try:
        success = future.result()
    except Exception as exc:
        logger.exception('Task %s failed with exception: %s', claimed_file.name, exc)
        success = False

    _, _, _, done_dir, blocked_dir = _workflow_directories()
    if success:
        _move_to_folder(claimed_file, done_dir)
        audit.log_action('task_complete', claimed_file.stem, {'worker_id': WORKER_ID}, status='success')
    else:
        _move_to_folder(claimed_file, blocked_dir)
        audit.log_action('task_complete', claimed_file.stem, {'worker_id': WORKER_ID}, status='blocked', result='ralph_loop_failed')

    update_dashboard()


def process_running_tasks() -> None:
    """Finalize any claimed tasks whose background worker future has completed."""
    for claimed_file, future in list(PENDING_TASKS.items()):
        if not future.done():
            continue

        _handle_completed_future(future, claimed_file)
        del PENDING_TASKS[claimed_file]


def process_needs_action():
    """Check /Needs_Action and process pending tasks using a claim-before-run model."""
    needs_action_dir, _, _, _, _ = _workflow_directories()
    if not needs_action_dir.exists():
        return

    for file in sorted(needs_action_dir.glob('*.md')):
        try:
            content = file.read_text(encoding='utf-8')
            if 'status: pending' not in content:
                continue

            task_id = file.stem
            logger.info('Found pending task: %s', task_id)

            claimed_file = claim_task(file)
            if claimed_file is None:
                continue

            prompt = f"Process the file '{claimed_file.name}'. Content:\n{content}"
            future = TASK_EXECUTOR.submit(run_ralph_loop, task_id, prompt)
            PENDING_TASKS[claimed_file] = future
        except Exception as exc:
            logger.error('Error processing file %s: %s', file, exc)


def check_approvals():
    """Check if any files moved to /Approved and execute them."""
    _, approved_dir, _, _, _ = _workflow_directories()
    if not approved_dir.exists():
        return

    for file in approved_dir.glob('*.md'):
        try:
            content = file.read_text(encoding='utf-8')
            if 'type: linkedin_post' in content or 'type: linkedin_feed_item' in content:
                continue

            logger.info('Found approved action: %s', file.name)
            run_claude_task(
                f"Read {file} and execute the approved action using tools. Then move the file to /Done.",
                task_file=file,
            )
        except Exception as exc:
            logger.error('Error checking approvals: %s', exc)


def generate_linkedin_post():
    logger.info('Generating LinkedIn post...')
    run_claude_task(
        'Use the post_to_linkedin skill to create a new LinkedIn post draft.'
    )


def update_dashboard():
    logger.info('Updating dashboard...')
    run_claude_task(
        'Update Dashboard.md with current status of Needs_Action, Done, and Logs.'
    )


schedule.every(60).seconds.do(process_needs_action)
schedule.every(10).seconds.do(process_running_tasks)
schedule.every(2).minutes.do(check_approvals)
schedule.every(10).minutes.do(update_dashboard)
schedule.every().monday.at('09:00').do(generate_linkedin_post)
schedule.every().thursday.at('09:00').do(generate_linkedin_post)

logger.info('Production-oriented orchestrator started.')


if __name__ == '__main__':
    try:
        _ensure_runtime_prerequisites()
    except Exception as exc:
        logger.error('Startup check failed: %s', exc)
        raise SystemExit(1) from exc

    while True:
        schedule.run_pending()
        time.sleep(1)
